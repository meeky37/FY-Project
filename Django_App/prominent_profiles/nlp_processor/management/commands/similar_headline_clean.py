from django.core.management.base import BaseCommand
from profiles_app.models import Article
import Levenshtein
from bs4 import BeautifulSoup


class Command(BaseCommand):
    """
    Identifies and deletes duplicate or very similar articles based on  Levenshtein distance
    calculations of their headlines and author names. This command processes all articles in the
    database, comparing each pair of articles to determine their similarity.

    Articles are considered duplicates if their headlines and author names are similar within
    defined thresholds. The command supports both automatic deletion (based on strict thresholds)
    and manual review (based on more lenient thresholds) for identifying similar articles.

    For strictly similar articles (under strict thresholds), the article with the higher ID is
    automatically deleted. For articles that are similar under more lenient thresholds, the command
    prompts for manual review to decide whether to delete the article with the higher ID.

    The command uses BeautifulSoup to parse and clean the HTML content of article headlines before
    comparison. Levenshtein distance is used to quantify the similarity between the cleaned headlines
    and author names.

    NB: This command was designed before the more complex ArticleStatistics and SimilarArticlePairs
    solution was devised for handling article similarity. It serves as a legacy method for
    managing duplicate articles.
    """

    help = 'Delete duplicate/very similar articles automatically / via manual review'

    def handle(self, *args, **options):
        articles = Article.objects.all()

        for i, article1 in enumerate(articles):
            for article2 in articles[i + 1:]:

                html_content = article1.headline.lower().strip()
                soup = BeautifulSoup(html_content, 'html.parser')
                article_1_headline = soup.get_text()

                html_content = article2.headline.lower().strip()
                soup = BeautifulSoup(html_content, 'html.parser')
                article_2_headline = soup.get_text()

                distance = Levenshtein.distance(article_1_headline,
                                                article_2_headline)

                strict_headline_similarity_threshold = 5
                strict_author_similarity_threshold = 3

                headline_similarity_threshold = 10
                author_similarity_threshold = 3

                if distance < strict_headline_similarity_threshold and (
                        article1.author is not None and
                        article2.author is not None and
                        Levenshtein.distance(article1.author.lower().strip(),
                                             article2.author.lower().strip()) <
                        strict_author_similarity_threshold
                ):

                    self.stdout.write(self.style.SUCCESS(
                        f'Article ID {article1.id}: {article_1_headline}, {article1.author}  '
                        f'published by:  '
                        f'{article1.site_name} is similar to Article ID {article2.id}:'
                        f' {article_2_headline}, {article2.author} published by: '
                        f' {article2.site_name}'))

                    print('Article with the higher ID will be deleted... ')

                    try:
                        if article1.id > article2.id:
                            article_to_delete = article1
                        else:
                            article_to_delete = article2

                        article_to_delete.delete()
                    except Exception:
                        print("Error Occurred")


                elif distance < headline_similarity_threshold and (
                        article1.author is not None and
                        article2.author is not None and
                        Levenshtein.distance(article1.author.lower().strip(),
                                             article2.author.lower().strip()) <
                        author_similarity_threshold) and (
                        article1.site_name is not None and
                        article2.site_name is not None and
                        article1.site_name == article2.site_name):
                    print(f'headline distance: {distance}')

                    self.stdout.write(self.style.SUCCESS(
                        f'Article ID {article1.id}: {article_1_headline}, {article1.author}  '
                        f'published by:  '
                        f'{article1.site_name} is similar to Article ID {article2.id}:'
                        f' {article_2_headline}, {article2.author} published by: '
                        f' {article2.site_name}'))

                    print('Article with the higher ID will be deleted... ')

                    try:
                        if article1.id > article2.id:
                            article_to_delete = article1
                        else:
                            article_to_delete = article2

                        article_to_delete.delete()
                    except Exception:
                        print("Error Occurred")

                elif distance < headline_similarity_threshold and (
                        article1.author is not None and
                        article2.author is not None and
                        Levenshtein.distance(article1.author.lower().strip(),
                                             article2.author.lower().strip()) <
                        author_similarity_threshold
                ):
                    print(f'headline distance: {distance}')

                    self.stdout.write(self.style.SUCCESS(
                        f'Article ID {article1.id}: {article_1_headline}, {article1.author}  '
                        f'published by:  '
                        f'{article1.site_name} is similar to Article ID {article2.id}:'
                        f' {article_2_headline}, {article2.author} published by: '
                        f' {article2.site_name}'))

                    delete_higher_id = input(
                        'Do you want to delete the article with the higher ID? (y/n): ')

                    try:
                        if delete_higher_id.lower() == 'y':
                            if article1.id > article2.id:
                                article_to_delete = article1
                            else:
                                article_to_delete = article2

                            article_to_delete.delete()
                    except:
                        print("Error Occurred")

        self.stdout.write(self.style.SUCCESS('Similar articles check complete'))


"""
Example Output:
                                  
(Project) ameek@Anthonys-Laptop prominent_profiles % python manage.py similar_headline_clean
Article ID 222: rishi sunak accused of misleading public over tory campaign questionnaire landing on doorsteps, Kate Devlin  published by:  The Independent is similar to Article ID 373: rishi sunak accused of misleading public over tory campaign questionnaire landing on doorsteps, Kate Devlin published by:  Yahoo News
Article with the higher ID will be deleted... 
Article ID 286: prince harry ‘won’t spend christmas with charles or william’ after endgame drama – while others given first time invite, Harry Goodwin  published by:  The Sun is similar to Article ID 336: prince harry ‘won’t spend christmas with charles or william’ after endgame drama – while others given first time invite, Harry Goodwin published by:  The Irish Sun
Article with the higher ID will be deleted... 
Article ID 310: meghan markle and prince harry have shared their 2023 holiday card, Emily Burack  published by:  Yahoo Life is similar to Article ID 344: meghan markle and prince harry have shared their 2023 holiday card, Emily Burack published by:  Yahoo Life
Article with the higher ID will be deleted... 
Article ID 374: sunak accused of toxic rhetoric after warning of ‘overwhelming’ migration to europe, Angela Giuffrida; Michael Savage  published by:  The Guardian is similar to Article ID 389: sunak accused of toxic rhetoric after warning of ‘overwhelming’ migration to europe, Angela Giuffrida; Michael Savage published by:  The Guardian
Article with the higher ID will be deleted... 
Article ID 423: harry and meghan release 2023 holiday card, Chaya Tong  published by:  The Daily Beast is similar to Article ID 452: harry and meghan release 2023 holiday card, Chaya Tong published by:  Yahoo Sport
Article with the higher ID will be deleted... 
headline distance: 5
Article ID 474: sunak will face another by-election as mp peter bone recalled over sex misconduct, Nick Duffy  published by:  inews.co.uk is similar to Article ID 476: sunak will face another by-election as tory mp peter bone recalled over sex misconduct, Nick Duffy published by:  inews.co.uk
Article with the higher ID will be deleted... 
Article ID 482: rishi sunak slammed by statistics watchdog over misleading debt claims, Kevin Schofield  published by:  Yahoo News is similar to Article ID 517: rishi sunak slammed by statistics watchdog over misleading debt claims, Kevin Schofield published by:  HuffPost UK
Article with the higher ID will be deleted... 
Article ID 521: meghan markle reveals the one gift archie wants—but isn’t getting—for christmas, Alyssa Bailey  published by:  Yahoo Movies is similar to Article ID 568: meghan markle reveals the one gift archie wants—but isn’t getting—for christmas, Alyssa Bailey published by:  Yahoo Life
Article with the higher ID will be deleted... 
Article ID 547: there's speculation around meghan markle's return to the royal family & it doesn't make sense, Kristyn Burtt  published by:  Yahoo Entertainment is similar to Article ID 574: there’s speculation around meghan markle’s return to the royal family & it doesn’t make sense, Kristyn Burtt published by:  SheKnows
Article with the higher ID will be deleted... 
Article ID 553: meghan markle says prince archie might not get his christmas wish, Condé Nast; Erin Vanderhoof  published by:  Glamour UK is similar to Article ID 901: meghan markle says prince archie might not get his christmas wish, Condé Nast; Erin Vanderhoof published by:  Vanity Fair
Article with the higher ID will be deleted... 
Article ID 555: meghan markle shares christmas present she's refusing to get son archie, Rebecca Russell; Mollie Quirk  published by:  OK! Magazine is similar to Article ID 1167: meghan markle shares christmas present she's refusing to get son archie, Rebecca Russell; Mollie Quirk published by:  OK! Magazine
Article with the higher ID will be deleted... 
Article ID 557: meghan markle lets slip what archie wants for christmas - and why he won't be getting it, Jennifer Newton  published by:  Irish Mirror is similar to Article ID 570: meghan markle lets slip what archie wants for christmas - and why he won't be getting it, Jennifer Newton published by:  Irish Mirror
Article with the higher ID will be deleted... 
headline distance: 7
Article ID 557: meghan markle lets slip what archie wants for christmas - and why he won't be getting it, Jennifer Newton  published by:  Irish Mirror is similar to Article ID 884: meghan markle lets slip what prince archie wants for christmas - and why he won't be getting it, Jennifer Newton published by:  The Mirror
Do you want to delete the article with the higher ID? (y/n): y
headline distance: 7
Article ID None: meghan markle lets slip what archie wants for christmas - and why he won't be getting it, Jennifer Newton  published by:  Irish Mirror is similar to Article ID None: meghan markle lets slip what prince archie wants for christmas - and why he won't be getting it, Jennifer Newton published by:  The Mirror
Do you want to delete the article with the higher ID? (y/n): y
Error Occurred
Article ID 616: new eu anti-migrant deal will help rishi sunak ‘stop the boats’, claims french politician, Andy Gregory  published by:  The Independent is similar to Article ID 622: new eu anti-migrant deal will help rishi sunak ‘stop the boats’, claims french politician, Andy Gregory published by:  Yahoo News
Article with the higher ID will be deleted... 
Article ID 712: meghan markle and prince harry jet to tropical holiday vacation with prince archie and princess lilibet, Janine Henni  published by:  Yahoo News is similar to Article ID 738: meghan markle and prince harry jet to tropical holiday vacation with prince archie and princess lilibet, Janine Henni published by:  PEOPLE
Article with the higher ID will be deleted... 
Article ID 729: prince harry and meghan markle seen on vacation with kids in costa rica, Aimée Lutkin  published by:  Yahoo Finance is similar to Article ID 746: prince harry and meghan markle seen on vacation with kids in costa rica, Aimée Lutkin published by:  Yahoo News
Article with the higher ID will be deleted... 
Article ID 799: how harry and meghan will spend christmas this year, Maanya Sachdeva  published by:  Yahoo News is similar to Article ID 828: how harry and meghan will spend christmas this year, Maanya Sachdeva published by:  Yahoo News
Article with the higher ID will be deleted... 
Article ID 877: meghan markle revealed the one gift she won't be giving to her son archie this christmas, Tessa Petak  published by:  Yahoo Movies is similar to Article ID 918: meghan markle revealed the one gift she won't be giving to her son archie this christmas, Tessa Petak published by:  Yahoo Life
Article with the higher ID will be deleted... 
Article ID 974: block truss’s resignation honours, sunak urged ahead of list being published, Hugo Gye  published by:  inews.co.uk is similar to Article ID 997: block truss’s resignation honours, sunak urged ahead of list being published, Hugo Gye published by:  inews.co.uk
Article with the higher ID will be deleted... 
Article ID 1032: 'royal christmas a world away from harry and meghan's californian life', says ex-chef, Anna Pointer; Rebecca Russell  published by:  OK! Magazine is similar to Article ID 1063: 'royal christmas a world away from harry and meghan's californian life', says ex-chef, Anna Pointer; Rebecca Russell published by:  OK! Magazine
Article with the higher ID will be deleted... 
Article ID 1035: prince harry's attacks on the press are 'misguided' and 'paranoid', nicholas witchell says, Hayley Dixon  published by:  Yahoo News is similar to Article ID 1067: prince harry's attacks on the press are 'misguided' and 'paranoid', nicholas witchell says, Hayley Dixon published by:  Yahoo News
Article with the higher ID will be deleted... 
Article ID 1086: 2023 politics wrapped: how much of this nonsense do you remember?, Ned Simons  published by:  HuffPost UK is similar to Article ID 1109: 2023 politics wrapped: how much of this nonsense do you remember?, Ned Simons published by:  Yahoo News
Article with the higher ID will be deleted... 
Article ID 1144: prince andrew attends royal christmas as ex-wife sarah ferguson joins for first time since 1990s, Stephanie Petit  published by:  Yahoo News is similar to Article ID 1171: prince andrew attends royal christmas as ex-wife sarah ferguson joins for first time since 1990s, Stephanie Petit published by:  Yahoo Sport
Article with the higher ID will be deleted... 
Article ID 1239: did u.k. prime minister rishi sunak snub prince harry in his christmas video?, Stephanie Petit  published by:  Yahoo Movies is similar to Article ID 1273: did u.k. prime minister rishi sunak snub prince harry in his christmas video?, Stephanie Petit published by:  Yahoo Life
Article with the higher ID will be deleted... 
Article ID 1343: kate middleton has 'moved on' from drama with prince harry and meghan markle, says friend (exclusive), Monique Jessen; Simon Perry  published by:  Yahoo News is similar to Article ID 1380: kate middleton has 'moved on' from drama with prince harry and meghan markle, says friend (exclusive), Monique Jessen; Simon Perry published by:  Yahoo Movies
Article with the higher ID will be deleted... 
Article ID 1345: meghan markle and prince harry's relationship timeline, Alicia Brunker  published by:  Yahoo Movies is similar to Article ID 1382: meghan markle and prince harry's relationship timeline, Alicia Brunker published by:  Yahoo News
Article with the higher ID will be deleted... 
Similar articles check complete


"""
