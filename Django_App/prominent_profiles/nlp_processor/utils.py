from profiles_app.models import Entity #, Mention, Sentiment


class DatabaseUtils:
    @staticmethod
    def insert_entity(entity_name, source_article_id=None):
        try:
            existing_entity = Entity.objects.filter(name=entity_name).first()

            if existing_entity is not None:
                # Return to prevent duplicate entity creation later
                return existing_entity.id
            else:
                # Insert if entity does not exist (name match)
                new_entity = Entity(name=entity_name, type=None,
                                    source_article_id=source_article_id)
                new_entity.save()
                return new_entity.id
        except Exception as e:
            print("Error:", e)
