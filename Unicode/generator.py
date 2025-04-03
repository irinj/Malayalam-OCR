import os


class SafeList(list):
    def __getitem__(self, key):
        if key < len(self):
            return list.__getitem__(self, key)
        else:
            return ''

def generate(labels):
    print("Generating Unicode")
    path = os.getcwd()
    f = open(os.path.join(path, "output.txt"), 'w', encoding="utf-8")

    text = ""
    ending_symbols = {'ാ', 'ി', 'ീ', 'ു', 'ൂ', 'ൃ', 'ൗ', '്'}  
    previous_word = ""  

    for word in labels:
        i = 0
        word = SafeList(word)
        if word[0] in ending_symbols and not previous_word:
            continue  
        if word[0] in ending_symbols and previous_word:
            text = text.rstrip()  
        else:
            if previous_word:
                f.write(previous_word + " ")  
            text = ""

        while i < len(word):
            if word[i] == '*':
                text += "ം"
                i+=1
                
                
            if word[i] == 'െ':
                if word[i + 1] == 'െ':
                    text += word[i + 2] + 'ൈ'
                    i += 2
                else:
                    text += word[i + 1]
                    if i + 2 < len(word) and word[i + 2] == 'ാ':
                        text += 'ൊ'
                        i += 2
                    else:
                        text += 'െ'
                        i += 1
            elif word[i] == 'േ':
                text += word[i + 1]
                if i + 2 < len(word) and word[i + 2] == 'ാ':
                    text += 'ോ'
                    i += 2
                else:
                    text += 'േ'
                    i += 1
            elif word[i] == '്ര':
                text += word[i + 1] + '്ര'
                i += 1
                
                
            elif word[i] in ending_symbols and text[-1] in ending_symbols:
                i+=1
            else:
                text += word[i]
            i += 1
        
        text = text.replace("ഇൗ", "ഈ")
        text = text.replace("ഒാ", "ഓ")
        text = text.replace("ഒൗ", "ഔ")
        previous_word = text  
    
    if previous_word:
        f.write(previous_word)

    f.close()
    print("Generated output")
