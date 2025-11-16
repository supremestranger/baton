code = ""

with open("E:\\UnityProjects\\baton\\web-app\\main2.py", "r") as file:
    code += file.read()

print(repr(code))