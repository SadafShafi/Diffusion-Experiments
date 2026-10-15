

from models import Model
from helpers import save_image




my_model = Model("segmind/tiny-sd")

prompts = ["",""," "]

answers =[]
times = []
for x in prompts:
    answers.append(my_model.inference(x))
    times.append(my_model.return_time())

for answer,prompt,ti in zip(answers,prompts,times):
    save_image(answer, name=prompt+" "+str(ti))
