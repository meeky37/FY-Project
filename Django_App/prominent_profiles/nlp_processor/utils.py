from profiles_app.models import Entity, BoundMention, Article , OverallSentiment


class DatabaseUtils:
    @staticmethod
    def insert_entity(entity_name, source_article_id=None):
        try:
            existing_entity = Entity.objects.filter(name=entity_name).first()

            article_instance = Article.objects.get(id=source_article_id)

            if existing_entity is not None:
                # Return to prevent duplicate entity creation later
                return existing_entity.id
            else:
                # Insert if entity does not exist (name match)
                new_entity = Entity(source_article=article_instance, name=entity_name, type=None)
                new_entity.save()
                return new_entity.id
        except Exception as e:
            print("Error:", e)

    @staticmethod
    def insert_bound_mention_data(entity_name, article_id, entity_db_id, scores, text,
                                  bounds_keys):
        try:
            # Retrieve or create Article and Entity instances
            article_instance, created_article = Article.objects.get_or_create(id=article_id)
            entity_instance, created_entity = Entity.objects.get_or_create(id=entity_db_id)

            # Extract values
            bound_start = bounds_keys[0]
            bound_end = bounds_keys[1]
            avg_neutral, avg_positive, avg_negative = scores
            bound_text = text

            # Create BoundMention instance
            bound_mention_instance, inserted = BoundMention.objects.get_or_create(
                article=article_instance,
                entity=entity_instance,
                bound_start=bound_start,
                bound_end=bound_end,
                avg_neutral=avg_neutral,
                avg_positive=avg_positive,
                avg_negative=avg_negative,
                bound_text=bound_text
            )

            # print("Data inserted successfully for entity:", entity_name)

        except Exception as e:
            print(f"Error inserting data for entity {entity_name}:", e)

    @staticmethod
    def insert_overall_sentiment(article_id, entity_id, num_bound, linear_neutral,
                                 linear_positive, linear_negative, exp_neutral, exp_positive,
                                 exp_negative):
        try:
            # Retrieve or create Article and Entity instances
            article_instance, created_article = Article.objects.get_or_create(id=article_id)
            entity_instance, created_entity = Entity.objects.get_or_create(id=entity_id)

            # Create OverallSentiment instance
            overall_sentiment_instance = OverallSentiment.objects.get_or_create(
                article=article_instance,
                entity=entity_instance,
                num_bound=num_bound,
                linear_neutral=linear_neutral,
                linear_positive=linear_positive,
                linear_negative=linear_negative,
                exp_neutral=exp_neutral,
                exp_positive=exp_positive,
                exp_negative=exp_negative
            )

            # print("Data inserted successfully into 'OverallSentiment' table.")

        except Exception as e:
            print("Error inserting data into 'OverallSentiment' table:", e)
