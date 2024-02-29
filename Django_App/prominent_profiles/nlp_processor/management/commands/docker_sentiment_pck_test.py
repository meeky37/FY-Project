from NewsSentiment import TargetSentimentClassifier
from django.core.management import BaseCommand
from fastcoref import FCoref

"""
This django command was created to rapidly test NewsSentiment and FastCorefs on the digital ocean 
droplet.

It helped verify the functionality and assess the computational feasibility of running these NLP 
models on the server's hardware, especially given considerations that are specific to configurations 
that may differ from my development environments, such as those specific to my Macbook e.g. MPS.

There would have been no point setting up celery, celery beat, redis etc. if it was eventually 
determined that the droplet wouldn't be powerful enough or the setup was awkward etc. then SFTP 
of data from my macbook would have been used instead. At least this enabled determination quickly so
efforts would not be wasted.
"""


class Command(BaseCommand):
    help = 'Test News MTSC and FastCoref works on docker/digital ocean setup'

    def handle(self, *args, **options):

        try:
            model = FCoref(device='cpu')
            preds = model.predict(texts=[
                'We are so happy to see you using our coref package. This package is very fast!'])
            output = preds[0].get_clusters(as_strings=True)
            print(output)
        except Exception as e:
            print(f"A FCoref error occurred: {e}")

        try:
            tsc = TargetSentimentClassifier()
            sentiment = tsc.infer_from_text('', 'Rishi Sunak',
                                            " is facing calls to apologise after joking about "
                                            "Labour's position on trans people when the mum of"
                                            " murdered teenager Brianna Ghey - who was transgender"
                                            " - was in Parliament.")
            print(sentiment[0])
        except Exception as e:
            print(f"A NewsSentiment error occurred: {e}")
