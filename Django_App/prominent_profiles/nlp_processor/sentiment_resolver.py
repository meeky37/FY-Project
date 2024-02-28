import time
import warnings


from intervaltree import Interval, IntervalTree
from NewsSentiment import TargetSentimentClassifier
from NewsSentiment.customexceptions import TooLongTextException

from .models import BoundError
from .utils import DatabaseUtils

from decimal import Decimal, ROUND_HALF_UP
from .constants import EXPONENTIAL_K_VALUE



def scaling(avg_array_list, k=3, linear=False):
    """
    Scales the average sentiment scores by applying either linear or exponential scaling.

    Args:
        avg_array_list (list of list of float): A list of average sentiment scores for different categories.
        k (int, optional): The exponent used for scaling when linear is False. Defaults to 3.
        linear (bool, optional):  True -> apply linear scaling. False ->  apply exponential scaling.

    Returns:
        list: Scaled sentiment scores as a list containing [neutral_points, positive_points, negative_points].
    """
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
    """
    Calculates the average sentiment scores for neutral, positive, and negative sentiments 
    from a list of probability data.

    Iterates through the sentiment analysis results for each bound (a text segment) 
    to calculate a mean sentiment across all input probabilities.

    Args:
        probabilities (list of dict): A list where each element is a dictionary containing
            'class_prob' (the probability score) and 'class_label' (the sentiment label which
            can be 'neutral', 'positive', or 'negative').

    Returns:
        list: A list containing the avg probability scores for [neutral, positive, negative]
            sentiments. Each avg is computed as the total accumulated probability for the
            sentiment divided by the number of entries in the input list. 
            Empty lists will return [0, 0, 0].
    """
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
    """
    Elements of the array rounded to one dp with adjustment for a sum of 100
    
     Args:
        arr (list of float): The input array to be rounded.

    Returns:
        list: The rounded array with elements rounded to one decimal place, adjusted to sum up to 100.
    """
    decimal_array = [Decimal(str(x)) for x in arr]
    rounded_array = [x.quantize(Decimal('0.0'), rounding=ROUND_HALF_UP) for x in decimal_array]
    rounded_sum = sum(rounded_array)
    adjustment = Decimal('100') - rounded_sum
    rounded_array[-1] += adjustment
    rounded_array = [float(x) for x in rounded_array]
    return rounded_array


def percentage_contribution(elements):
    """
    Calculates the % contribution of each element in a list to the total sum of the list.

    Args:
        elements (list of float): A list of numerical values.

    Returns:
        list: A list of percentage contributions of each element, rounded to one decimal place.
    """
    total = sum(elements)
    percentage_contributions = [(element / total) * 100 for element in elements]
    return round_array_to_1dp(percentage_contributions)


def log_bound_error(exception, article_id, mention_start, mention_end, left_segment,
                    mention_segment, right_segment):
    """Logs details about the text bound error to the database."""
    if isinstance(exception, TooLongTextException):
        error_message = "TooLongTextException"
    else:
        error_message = "Exception during sentiment analysis"

    BoundError.objects.get_or_create(
        article_id=article_id,
        bound_start=mention_start,
        bound_end=mention_end,
        left_segment=left_segment,
        mention_segment=mention_segment,
        right_segment=right_segment,
        error_message=error_message
    )


class SentimentAnalyser:
    """
    For analysing the sentiment of entities within article text using NewsSentiment and tools to
    get the clusters in the correct form.
    """

    def __init__(self):
        self.tsc = TargetSentimentClassifier()

    def bounds_sentiment(self, mention_start, mention_end, sentence_start, sentence_end,
                         article_text, database_id):
        """
        Analyses sentiment for a specific text segment (mention) within an article using
        NewsSentiment.

        Args:
            mention_start (int): The start index of the mention within the article text.
            mention_end (int): The end index of the mention within the article text.
            sentence_start (int): The start index of the sentence containing the mention.
            sentence_end (int): The end index of the sentence containing the mention.
            article_text (str): The full text of the article.
            database_id (int): The database ID of the article.

        Returns:
            dict: A dictionary containing the sentiment analysis results for the mention.
                  Returns None if an error occurs during analysis.

        Exceptions will result in the creation of BoundError object for later analysis, debugging
        and improvements to the tokenisation and entity clustering logic.
        """
        try:
            warnings.filterwarnings("ignore",
                                    message="The `pad_to_max_length` argument is deprecated and "
                                            "will be removed in a future version, use `padding=True`"
                                            " or `padding='longest'` to pad to the longest sequence"
                                            " in the batch, or use `padding='max_length'` to pad to"
                                            " a max length.")
            left_segment = article_text[sentence_start:mention_start]
            mention_segment = article_text[mention_start:mention_end]
            right_segment = article_text[mention_end:sentence_end]

            # Could add logging here to see the quality of sentence segmentation.
            start_time = time.time()
            sentiment = self.tsc.infer_from_text(left_segment, mention_segment, right_segment)
            elapsed_time = time.time() - start_time

            if elapsed_time > 5:
                print(f"News Sentiment Time > 5 seconds so: {elapsed_time} seconds")
            # print(sentiment[0])

            return sentiment[0]

        except Exception as e:
            # print(f"LEFT: {left_segment}")
            # print(f"MENTION: {mention_segment}")
            # print(f"RIGHT: {right_segment}")
            log_bound_error(e, database_id, mention_start, mention_end, left_segment,
                            mention_segment, right_segment)
            return None

    def process_clustered_entities(self, clustered_entities, sentence_bounds, article_text,
                                   database_id,
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
                                                           article_text, database_id)

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
