# gpt-pet
A LLM Powered Pet that continuously explores, learns, and interacts with people and animals.

Heavily inspired from [Voyager](https://github.com/MineDojo/Voyager), GPTPet has the following architecture.

![GPTPet drawio (1)](https://github.com/pj0620/gpt-pet/assets/37814424/994354cf-30c2-43c2-8606-7b8883a457fc)

# Installation Instructions
1. clone this git repo `git clone git@github.com:pj0620/gpt-pet.git`
2. start Docker deamon
3. Once Docker is started, run `docker-compose up` in the gpt-pet directory. This should install for a long time.
4. install requirements from requirements.txt
     `python -m pip install -r requirements.txt`
6. create a new file named '.env'
7. add the following to .env `OPENAI_API_KEY=<INSERT YOUR OPENAI KEY>`
8. run main.py through pycharm's launcher with the following settings. The important thing is to point it to your .env file.
9. watch the Pet start walking!

## As one script
```
git clone git@github.com:pj0620/gpt-pet.git
cd gpt-pet
# !!!MAKE SURE DOCKER IS RUNNING!!!
docker-compose up &
python -m pip install -r requirements.txt
echo "OPENAI_API_KEY=<INSERT YOUR OPENAI KEY>" > .env
source .env
python main.py
```
