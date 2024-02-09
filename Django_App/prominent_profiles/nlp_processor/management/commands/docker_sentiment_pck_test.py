from NewsSentiment import TargetSentimentClassifier
from django.core.management import BaseCommand
from fastcoref import FCoref

from Django_App.prominent_profiles.nlp_processor.constants import F_COREF_DEVICE


class Command(BaseCommand):
    help = 'Test News MTSC and FastCoref works on docker setup (as some MAC mps configs!)'

    def handle(self, *args, **options):
        model = FCoref(device=F_COREF_DEVICE)

        preds = model.predict(
            texts=['We are so happy to see you using our coref package. This package is very fast!']
        )

        output = preds[0].get_clusters(as_strings=True)

        print(output)

        # tsc = TargetSentimentClassifier()
        # sentiment = tsc.infer_from_text('', 'Rishi Sunak', " is facing calls to apologise after joking about Labour's position on trans people when the mum of murdered teenager Brianna Ghey - who was transgender - was in Parliament.")
        # print(sentiment[0])