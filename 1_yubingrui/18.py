#题目：两个乒乓球队进行比赛，各出三人。甲队为a,b,c三人，乙队为x,y,z三人。已抽签决定比赛名单。有人向队员打听比赛的名单。a说他不和x比，c说他不和x,z比，请编程序找出三队赛手的名单。  

jia_team = ["a","b","c"]
yi_team = ["x","y","z"]
combine = []
#c不和x,z比
for i in yi_team:
    if i != "x" and i != "z":
        combine.append(("c",i))
        jia_team.remove("c")
        yi_team.remove(i)
#a不和x比
for i in yi_team:
    if i != "x":
        combine.append(("a",i))
        jia_team.remove("a")
        yi_team.remove(i)

combine.append((jia_team[0],yi_team[0]))
print(combine)
