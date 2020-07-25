from config.config import cluster
from models.mongo import 

import discord
import string
import time
import random

class Quiz:
    """Quiz class."""
    def __init__(self,
            name:str,
            creator:str,
            owners:str,
            timestamp:float=time.time(),
            questions:list=[],
            seed:int=random.randint(1e9, 1e10-1),
            n=0
        ):
        """Create a quiz using the list of questions."""
        self.question = questions
        self.n = n

    def __iter__(self):
        """Iterate the questions through the quiz."""
        self.n = 0
        return self

    def __next__(self):
        """Return the next question."""
        if self.n < len(self.questions):
            self.n += 1
            return self.questions[self.n]
        else:
            raise StopIteration

    @property
    def shuffled_questions(self):
        """Return the shuffled list of questions of the quiz."""
        questions = self.questions[::]
        random.shuffle(questions)
        return questions

class Question:
    """Representation of a question of a quiz.
    This object is not strictely speaking a question as it also contains
    the possible answers and good answer for the real question."""

    def __init__(self,
            question:str,
            answers:list=[],
            color:discord.Color=None,
            url:str=None,
            description:str=None,
            image:str=None,
            thumbnail:str=None,
            footer:str=None,
            timestamp:time.time(),

        ):
        """Create a question using ."""
        self.question = question
        self.answers = answers
        self.color = color
        self.url = url
        self.description = description
        self.image = image
        self.thumbnail = thumbnail
        self.footer = footer
        self.timestamp = timestamp

    @property 
    def answer(self):
        """Right answer."""
        return self.answers[0]
    
    @property
    def title(self):
        """Title of the discord embed associated with the question."""
        return self.question

    @property
    def shuffled_answers(self):
        """Return a shuffled list of the possible answers."""
        answers = self.answers[::]
        random.shuffle(answers)
        return answers

    @property
    def fields(self):
        """Fields of the question embed."""
        return {string.ascii_uppercase[i]:answer for i, answer in enumerate(self.shuffled_answers)}

    def embed(self):
        """Return an embed for the given question."""
        embed = discord.Embed(
            title=self.title,
            description=self.description,
            url=self.url,
            timestamp=self.timestamp,
            color=self.color,
        )
        for name, value in self.fields.items():
            embed.add_field(name=name, value=value)
        if self.image:
            embed.set_image(url=self.image)
        if self.thumbnail:
            embed.set_thumbnail(url=self.thumbnail)
        if self.footer:
            embed.set_footer(text=self.footer)
        return embed