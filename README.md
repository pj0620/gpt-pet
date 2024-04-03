# gpt-pet
A LLM Powered Pet that continuously explores, learns, and interacts with people and animals.

Heavily inspired from [Voyager](https://github.com/MineDojo/Voyager), GPTPet has the following architecture.

![GPTPet drawio (2)](https://github.com/pj0620/gpt-pet/assets/37814424/51339218-054b-4c18-86a2-cd04a634d3a3)

# Environment

By default, this project will run in a simulated house, and interact with the outside world via [Ai2Thor](https://github.com/allenai/ai2thor). However, the goal is to place this code inside a real robot and let it join the family just like any other pet. This is still in progress, I will continue to update as this is finished. The physical robot is being designed with [OnShape](https://www.onshape.com/en/). 

Link to GPTPet's [3d model](https://cad.onshape.com/documents/8d74c2e4639a24043b115b26/w/624b64a1b1fd7dfb5e1b20de/e/c549b3f286116a91b375a18b) 

<img width="400" alt="image" src="https://github.com/pj0620/gpt-pet/assets/37814424/645a1c9f-bb02-4f79-addb-7d3b4d878088">




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
