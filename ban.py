def find_sentence(fileName, findText):
    file = open(fileName, mode="r", encoding="utf8")

    result = []
    data = file.read()
    data = data.splitlines()

    for line in data:
        sentences = line.split("\n ")
        for sentence in sentences:
            sentence = sentence.strip("\n")
            if findText in sentence:
                result.append(sentence + "\n")

    file.close()
    return result

result = find_sentence("./userbanlist.txt", "내보냈습니다.")

temp = []
for sentence in result:
    temp.append(sentence.replace('님을 내보냈습니다.\n', ''))

temp = list(set(temp))
temp.sort()

with open('./blacklist.txt', mode="w", encoding="utf8") as f:
    for line in temp:
        f.write(line + "\n")