from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from faker import Faker
import random
from questions.models import Profile, Tag, Question, Answer, QuestionLike, AnswerLike


class Command(BaseCommand):
    help = 'Fill database with test data'

    def add_arguments(self, parser):
        parser.add_argument(
            'ratio',
            type=int,
            nargs='?',
            default=1,
            help='Coefficient for data volume'
        )

    def handle(self, *args, **options):
        ratio = options['ratio']
        fake = Faker()

        self.stdout.write(self.style.SUCCESS(f'Starting data generation with ratio={ratio}'))

        # Calculate counts
        num_users = ratio
        num_questions = ratio * 10
        num_answers = ratio * 100
        num_tags = ratio
        num_likes = ratio * 200

        # Create users
        self.stdout.write('Creating users...')
        users = []
        existing_usernames = set(User.objects.values_list('username', flat=True))
        for i in range(num_users):
            username = f"user_{i}"
            while username in existing_usernames:
                i += 1
                username = f"user_{i}"
            existing_usernames.add(username)
            user = User(
                username=username,
                email=f"user_{i}@example.com",
                first_name=fake.first_name(),
                last_name=fake.last_name(),
            )
            users.append(user)

        User.objects.bulk_create(users, batch_size=1000)
        users = list(User.objects.all())
        self.stdout.write(self.style.SUCCESS(f'Created {len(users)} users'))

        # Create profiles for users
        self.stdout.write('Creating profiles...')
        profiles = [Profile(user=user) for user in users]
        Profile.objects.bulk_create(profiles, batch_size=1000)
        self.stdout.write(self.style.SUCCESS(f'Created {len(profiles)} profiles'))

        # Create tags
        self.stdout.write('Creating tags...')
        tags = []
        tag_names = set()
        for _ in range(num_tags):
            while True:
                tag_name = fake.word()[:50]
                if tag_name not in tag_names:
                    tag_names.add(tag_name)
                    break
            tags.append(Tag(name=tag_name))

        Tag.objects.bulk_create(tags, batch_size=1000)
        tags = list(Tag.objects.all())
        self.stdout.write(self.style.SUCCESS(f'Created {len(tags)} tags'))

        # Create questions
        self.stdout.write('Creating questions...')
        questions = []
        user_ids = [u.id for u in users]

        for i in range(num_questions):
            question = Question(
                title=fake.sentence(nb_words=5)[:255],
                text=fake.sentence(nb_words=15)[:500],
                author_id=random.choice(user_ids),
                rating=random.randint(-10, 50),
            )
            questions.append(question)

        Question.objects.bulk_create(questions, batch_size=5000)
        self.stdout.write(self.style.SUCCESS(f'Created {num_questions} questions'))

        # Assign tags to questions
        self.stdout.write('Assigning tags to questions...')
        question_tags_data = []
        tag_ids = [t.id for t in tags]

        for question_id, question in enumerate(Question.objects.values_list('id', flat=True)):
            num_tags = random.randint(1, min(5, len(tags)))
            selected_tags = random.sample(tag_ids, k=num_tags)
            for tag_id in selected_tags:
                question_tags_data.append(Question.tags.through(question_id=question, tag_id=tag_id))

        Question.tags.through.objects.bulk_create(question_tags_data, batch_size=5000, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS('Assigned tags to questions'))

        # Create answers
        self.stdout.write('Creating answers...')
        answers = []
        question_ids = list(Question.objects.values_list('id', flat=True))

        for i in range(num_answers):
            answer = Answer(
                question_id=random.choice(question_ids),
                author_id=random.choice(user_ids),
                text=fake.sentence(nb_words=15)[:500],
                rating=random.randint(-10, 30),
            )
            answers.append(answer)

        Answer.objects.bulk_create(answers, batch_size=5000)
        self.stdout.write(self.style.SUCCESS(f'Created {num_answers} answers'))

        # Create question likes
        self.stdout.write('Creating question likes...')
        question_likes = []

        for _ in range(num_likes):
            question_likes.append(QuestionLike(
                user_id=random.choice(user_ids),
                question_id=random.choice(question_ids)
            ))

            if len(question_likes) >= 5000:
                QuestionLike.objects.bulk_create(question_likes, batch_size=5000, ignore_conflicts=True)
                question_likes = []

        if question_likes:
            QuestionLike.objects.bulk_create(question_likes, batch_size=5000, ignore_conflicts=True)

        question_likes_count = QuestionLike.objects.count()
        self.stdout.write(self.style.SUCCESS(f'Created {question_likes_count} question likes'))

        # Create answer likes
        self.stdout.write('Creating answer likes...')
        answer_ids = list(Answer.objects.values_list('id', flat=True))
        answer_likes = []

        for _ in range(num_likes):
            answer_likes.append(AnswerLike(
                user_id=random.choice(user_ids),
                answer_id=random.choice(answer_ids)
            ))

            if len(answer_likes) >= 5000:
                AnswerLike.objects.bulk_create(answer_likes, batch_size=5000, ignore_conflicts=True)
                answer_likes = []

        if answer_likes:
            AnswerLike.objects.bulk_create(answer_likes, batch_size=5000, ignore_conflicts=True)

        answer_likes_count = AnswerLike.objects.count()
        self.stdout.write(self.style.SUCCESS(f'Created {answer_likes_count} answer likes'))

        self.stdout.write(self.style.SUCCESS('Database filled successfully!'))
