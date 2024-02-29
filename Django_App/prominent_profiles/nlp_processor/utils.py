from profiles_app.models import Entity, BoundMention, Article , OverallSentiment


class DatabaseUtils:
    """
    A collection of static methods for database operations related to entities, bound mentions,
    and overall sentiments.
    Ensures data integrity and prevents duplicate entries by checking for existing records before
    insertion.
    """
    @staticmethod
    def insert_entity(entity_name, source_article_id=None):
        """
        Inserts a new entity into the database if it does not already exist.
        If the entity alreadyexists, it returns the existing entity's ID to prevent duplication
        and crucially allowing collections of articles to be attributed to the same entity
        building up their Prominent "Profile".

        :param entity_name: The name of the entity to insert.
        :param source_article_id: The ID of the article associated with the entity.
        :return: The ID of the existing or newly created entity.
        """
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
            print("Error inserting entity: ", e)

    @staticmethod
    def insert_bound_mention_data(entity_name, article_id, entity_db_id, scores, text,
                                  bounds_keys):
        """
        Inserts data for a bound mention of an entity within an article.
        If an identical record already exists, it prevents duplicate entries by not creating
        a new one. This can occur if the ci/cd is deployed over the droplet while this
        was running or if a out of memory error occurred (due to the initial 4GB droplet).

        :param entity_name:  The name of the entity.
        :param article_id:  The ID of the article where the mention is found.
        :param entity_db_id: The database ID of the entity.
        :param scores: A tuple containing average neutral, positive, and negative sentiment scores.
        :param text: The text of the mention and its context (ideally a single sentence).
        :param bounds_keys: A tuple containing the start and end positions of the context within
        the article.
        :return: N/A -> Inserts to DB instead.
        """
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
            BoundMention.objects.get_or_create(
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
        """
        Inserts data for a bound mention of an entity within an article.
        If an identical record already exists, it prevents duplicate entries by not creating
        a new one. This can occur if the ci/cd is deployed over the droplet while this
        was running or if an out of memory error occurred (due to the initial 4GB droplet).

        :param article_id: The ID of the article associated with the sentiment data.
        :param entity_id: The database ID of the entity.
        :param num_bound: The number of mentions (bounds) analyzed.
        :param linear_neutral: The linearly scaled neutral sentiment score.
        :param linear_positive: The linearly scaled positive sentiment score.
        :param linear_negative: The linearly scaled negative sentiment score.
        :param exp_neutral: The exponentially scaled neutral sentiment score.
        :param exp_positive: The exponentially scaled positive sentiment score.
        :param exp_negative: The exponentially scaled negative sentiment score.
        :return: N/A -> Inserts to DB instead.

        NB: Both scores are stored for flexibility if the app would prefer to adopt a linear
        scoring model, this means adjusting a Django View solely rather than having to
        reconfig/recalculate sentiment values. Both ways are coded in profiles_app/views.py
        """
        try:
            # Retrieve or create Article and Entity instances
            article_instance, created_article = Article.objects.get_or_create(id=article_id)
            entity_instance, created_entity = Entity.objects.get_or_create(id=entity_id)

            # Create OverallSentiment instance
            OverallSentiment.objects.get_or_create(
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
