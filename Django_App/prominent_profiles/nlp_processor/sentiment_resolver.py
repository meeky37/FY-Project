from decimal import Decimal, ROUND_HALF_UP
from .constants import EXPONENTIAL_K_VALUE
from intervaltree import Interval, IntervalTree
from NewsSentiment import TargetSentimentClassifier

from .models import BoundError
from .utils import DatabaseUtils


def scaling(avg_array_list, k=3, linear=False):
    neutral_points = positive_points = negative_points = 0

    for avg_array in avg_array_list:
        for i, avg_value in enumerate(avg_array):

            if linear:
                points = avg_value * 100
            else:
                points = (avg_value ** k) * 100

            if i == 0:
                neutral_points += points
            elif i == 1:
                positive_points += points
            elif i == 2:
                negative_points += points
    return [neutral_points, positive_points, negative_points]


def average_array(probabilities):
    num_probabilities = len(probabilities)
    neutral_total = positive_total = negative_total = 0

    for prob_data in probabilities:
        if not prob_data:
            continue
        class_prob = prob_data['class_prob']
        class_label = prob_data['class_label']

        if class_label == 'neutral':
            neutral_total += class_prob
        elif class_label == 'positive':
            positive_total += class_prob
        elif class_label == 'negative':
            negative_total += class_prob

    neutral_avg = neutral_total / num_probabilities if num_probabilities > 0 else 0
    positive_avg = positive_total / num_probabilities if num_probabilities > 0 else 0
    negative_avg = negative_total / num_probabilities if num_probabilities > 0 else 0

    return [neutral_avg, positive_avg, negative_avg]


def round_array_to_1dp(arr):
    decimal_array = [Decimal(str(x)) for x in arr]
    rounded_array = [x.quantize(Decimal('0.0'), rounding=ROUND_HALF_UP) for x in decimal_array]
    rounded_sum = sum(rounded_array)
    adjustment = Decimal('100') - rounded_sum
    rounded_array[-1] += adjustment
    rounded_array = [float(x) for x in rounded_array]
    return rounded_array


def percentage_contribution(elements):
    total = sum(elements)
    percentage_contributions = [(element / total) * 100 for element in elements]
    return round_array_to_1dp(percentage_contributions)


class SentimentAnalyser:

    def __init__(self):
        self.tsc = TargetSentimentClassifier()

    def bounds_sentiment(self, mention_start, mention_end, sentence_start, sentence_end,
                         article_text):
        try:
            left_segment = article_text[sentence_start:mention_start]
            mention_segment = article_text[mention_start:mention_end]
            right_segment = article_text[mention_end:sentence_end]

            # Could add logging here to see the quality of sentence segmentation.

            sentiment = self.tsc.infer_from_text(left_segment, mention_segment, right_segment)
            # print(sentiment[0])

            return sentiment[0]

        except Exception as e:
            print(f"Error during sentiment analysis: {e}")
            print(f"LEFT: {left_segment}")
            print(f"MENTION: {mention_segment}")
            print(f"RIGHT: {right_segment}")

            BoundError.objects.create(
                bound_start=mention_start,
                bound_end=mention_end,
                left_segment=left_segment,
                mention_segment=mention_segment,
                right_segment=right_segment,
                error_message=f"Exception during sentiment analysis: {e.with_traceback()}"
            )

            raise
            return None

    def process_clustered_entities(self, clustered_entities, sentence_bounds, article_text,
                                   debug):
        START_HIGHLIGHT = '\033[0m'
        END_HIGHLIGHT = '\033[94m'
        GREEN = '\033[92m'
        END_COLOR = '\033[0m'

        bounds_tree = IntervalTree(Interval(start, end) for start, end in
                                   sentence_bounds)

        bounds_sentiment = {}

        ''' Some entities at this point may not have been fully consolidated.
            Running the model is the most intensive part of this process.
            Since non consolidated entities likely have the same coref cluster.
            Running model over save cluster more than once is wasteful.'''

        cluster_id_mapping = {}  # Map cluster_id to bounds_sentiment

        for entity in clustered_entities:
            entity_name = entity['Entity Name']
            if 'entity_db_id' in entity:
                entity_db_id = entity['entity_db_id']
            else:
                print("Process clustered entities would skip...")
                print(entity_name)
                continue
            cluster_positions = entity['Cluster Info']['Cluster Positions']
            cluster_id = entity['Cluster Info']['Cluster ID']

            # Check if the cluster_id has been seen before
            if cluster_id in cluster_id_mapping:
                # print('Using cached bounds sentiment')
                # If so, use the cached bounds_sentiment
                for entry in cluster_id_mapping[cluster_id]:
                    bounds_key = entry['bounds_key']

                    if entity_name not in bounds_sentiment[bounds_key]:
                        bounds_sentiment[bounds_key][entity_name] = {}

                    if entity_db_id not in bounds_sentiment[bounds_key][entity_name]:
                        bounds_sentiment[bounds_key][entity_name][entity_db_id] = []

                    bounds_sentiment[bounds_key][entity_name][entity_db_id].append(entry['result'])

            else:
                cluster_id_mapping[cluster_id] = []

                for mention_start, mention_end in cluster_positions:
                    overlap = bounds_tree.overlap(mention_start, mention_end)
                    if overlap:
                        for interval in overlap:
                            sentence_start, sentence_end = interval.begin, interval.end
                            bounds_key = (sentence_start, sentence_end)

                            if bounds_key not in bounds_sentiment:
                                bounds_sentiment[bounds_key] = {}

                            if entity_name not in bounds_sentiment[bounds_key]:
                                bounds_sentiment[bounds_key][entity_name] = {}

                            if entity_db_id not in bounds_sentiment[bounds_key][entity_name]:
                                bounds_sentiment[bounds_key][entity_name][entity_db_id] = []

                            highlighted_text = (
                                    START_HIGHLIGHT +
                                    article_text[sentence_start:mention_start] + END_HIGHLIGHT +
                                    article_text[mention_start:mention_end] + START_HIGHLIGHT +
                                    article_text[mention_end:sentence_end] + END_HIGHLIGHT)

                            result = self.bounds_sentiment(mention_start, mention_end,
                                                           sentence_start, sentence_end,
                                                           article_text)

                            bounds_sentiment[bounds_key][entity_name][entity_db_id].append(
                                result)

                            cluster_id_mapping[cluster_id].append({
                                'bounds_key': bounds_key,
                                'result': result
                            })

                            if debug:
                                print(
                                    START_HIGHLIGHT + f"{entity_name} - Mention ({mention_start}, {mention_end}) is within bounds ({sentence_start}, {sentence_end})")
                                print(highlighted_text)
                                print(
                                    GREEN + f"NewsSentiment Candidateappearance{len(bounds_sentiment[bounds_key][entity_name][entity_db_id])}" + END_COLOR)

        return bounds_sentiment

    @staticmethod
    def average_sentiment_results(source_article_id, bounds_sentiment, article_text):
        if bounds_sentiment is None:
            print("Error: bounds_sentiment is None")
            return
        entity_averages = {}
        for bounds_key, entity_results in bounds_sentiment.items():
            for entity_name, entity_db_ids in entity_results.items():
                # print("Entity DB IDs: ")
                # print(entity_db_ids)
                for entity_db_id, results in entity_db_ids.items():

                    if not results:  # Empty results for an entity? Skip...
                        continue
                    # print(results)
                    avg = average_array(results)

                    # Store entity - bound mention - bound text - average result in database

                    if entity_name not in entity_averages:
                        entity_averages[entity_name] = {
                            "entity_db_ids": [entity_db_id],
                            "bounds_keys": [bounds_key],
                            "sentiment_scores": [avg],
                            "text": [article_text[bounds_key[0]:bounds_key[1]]],
                        }
                    else:
                        entity_averages[entity_name]["entity_db_ids"].append(entity_db_id)
                        entity_averages[entity_name]["bounds_keys"].append(bounds_key)
                        entity_averages[entity_name]["sentiment_scores"].append(avg)
                        entity_averages[entity_name]["text"].append(
                            article_text[bounds_key[0]:bounds_key[1]])

        # print('Sentiment Scores Format: [Neutral, Positive, Negative]')
        for entity_name, averages in entity_averages.items():
            entity_db_id = averages['entity_db_ids'][0]
            # print(f"Averages for {entity_name} (Entity DB ID: {entity_db_id}):")
            sentiment_scores = averages['sentiment_scores']
            text = averages['text']
            bounds_keys = averages['bounds_keys']

            for i, scores in enumerate(sentiment_scores):
                # print("Sentiment Scores:", scores)
                # print("Text:", text[i])
                # print("Bounds Keys:", bounds_keys[i])
                # print()

                DatabaseUtils.insert_bound_mention_data(entity_name, source_article_id,
                                                        entity_db_id,
                                                        scores, text[i],
                                                        bounds_keys[i])

            num_bound = len(averages['sentiment_scores'])
            scaled_classification = scaling(averages['sentiment_scores'],
                                            k=EXPONENTIAL_K_VALUE)

            # Can't scale an array of [0, 0, 0] -> Divide by zero error.
            if sum(scaled_classification) == 0:
                # print(scaled_classification)
                continue

            exp_percent = percentage_contribution(scaled_classification)

            linear_scaled_classification = scaling(averages['sentiment_scores'],
                                                   linear=True)
            linear_percent = percentage_contribution(
                linear_scaled_classification)

            DatabaseUtils.insert_overall_sentiment(source_article_id, entity_db_id, num_bound,
                                                   linear_percent[0],
                                                   linear_percent[1],
                                                   linear_percent[2],
                                                   exp_percent[0], exp_percent[1], exp_percent[2])
