import os

# search through subagents folder and find agents and all evals. Run them and save optimal prompt in db

agents_dir = "./subagents/"
assert os.path.exists(agents_dir), "Missing subagents folder"

agent_folders = []
for root, dirs, files in os.walk(agents_dir):
    for dir in dirs:
        dir = os.path.join(root, dir)
        if "agent.py" in os.listdir(dir):
            agent_folders.append(dir)

print(agent_folders)



