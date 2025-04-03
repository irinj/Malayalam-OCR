import os
import cv2
import numpy as np
from keras.models import load_model

def getLabels():
    print("Starting classification...")

    model_path = r"C:\Users\Irin\Downloads\final edit (2)\final edit\finalmodel.keras"
    if not os.path.exists(model_path):
        print(f"Error: Model file not found at {model_path}")
        return []

    model = load_model(model_path)

    labels = ['അ','ഖ','മ്മ','മ്ല','യ്യ','ല്ല','വ്വ','ശ്ശ',
              'ശ്ല','ശ്ച','ഷ്ട','സ്ല','ഗ','സ്സ','സ്റ്റ','സ്ഥ',
              'ഹ്മ','ഹ്ന','ഹ്ല','ള്ള','റ്റ','ൻ','ഘ','ൽ',
              'ർ','ൾ','ൺ','ന്ധ','ങ','ച','ഛ','ജ',
              'ഝ','ഞ','ട','ആ','ഠ','ഡ','ഢ','ണ',
              'ത','ഥ','ദ','ധ','ന','പ','ഇ','ഫ',
              'ബ','ഭ','മ','യ','ര','ല','വ','ശ',
              'ഷ','ഉ','സ','ഹ','ള','ഴ','റ','ാ',
              'ി','ീ','ു','ൂ','ഋ','ൃ','െ','േ',
              'ൗ','്','്യ','്ര','്വ','ക്ക','ക്ല','എ',
              'ക്ഷ','ക്ത','ഗ്ഗ','ഗ്ല','ഗ്ന','ഗ്മ','ങ്ക','ങ്ങ',
              'ച്ച','ച്ഛ','ഏ','ജ്ജ','ജ്ഞ','ഞ്ച','ഞ്ഞ','ട്ട',
              'ഡ്ഡ','ണ്ട','ണ്ഡ','ണ്മ','ണ്ണ','ഒ','ത്ത','ത്ഥ',
              'ത്ഭ','ത്സ','ത്മ','ദ്ദ','ദ്ധ','ൻ്റ','ന്ത','ന്ദ',
              'ക','ന്ന','ന്മ','ന്ഥ','പ്പ','പ്ല','ബ്ബ','ബ്ല','ബ്ദ','മ്പ','ഡ്ഢ','ഫ്ല','ബ്ധ','സ്ധ']                   
    path = r"C:\Users\Irin\Downloads\final edit (2)\final edit\word"
    if not os.path.exists(path):
        print(f"Error: Image directory not found at {path}")
        return []

    try:
        dir_list = sorted(os.listdir(path), key=lambda x: int(x) if x.isdigit() else float('inf'))
    except ValueError as e:
        print(f"Error sorting directory files: {e}")
        return []

    height_data = {}
    height_file = "char_heights.txt"
    height_adjust_1=['ി','ീ','്യ','്ര']   
    height_adjust_2=['ു','ൂ','േ']

    if not os.path.exists(height_file):
        print(f"Error: Height file {height_file} not found!")
        return []

    with open(height_file, "r") as f:
        for line in f:
            key, value = line.strip().split(",")
            height_data[key] = int(value)

    Sreq = 30
    word_images = []  
    word_heights = []  

    for word_index, item in enumerate(dir_list):
        item_path = os.path.join(path, item)
        if not os.path.isdir(item_path):
            continue  

        try:
            d = sorted(os.listdir(item_path), key=lambda x: int(os.path.splitext(x)[0]) if x.split('.')[0].isdigit() else float('inf'))
        except ValueError as e:
            print(f"Error sorting images in {item_path}: {e}")
            continue
        total_confidences = []  

        char_images = []
        char_heights = []  

        for char_index, image_file in enumerate(d):
            image_path = os.path.join(item_path, image_file)
            image = cv2.imread(image_path, 0)

            if image is None:
                print(f"Warning: Unable to read image {image_path}. Skipping...")
                continue

            try:
                resized = cv2.resize(image, (Sreq, Sreq), interpolation=cv2.INTER_CUBIC)
                inverted = 255 - resized  
                normalized = inverted.astype('float32') / 255.0
                reshaped = normalized.reshape(Sreq, Sreq, 1)
                
                char_images.append(reshaped)

                char_key = f"{word_index+1}_{char_index+1}"
                char_heights.append(height_data.get(char_key, 0)) 

            except Exception as e:
                print(f"Error processing image {image_path}: {e}")

        word_images.append(char_images)
        word_heights.append(char_heights)  

    total_images = sum(len(word) for word in word_images)
    if total_images == 0:
        print("No valid images found for classification.")
        return []

    print("Performing classification...")
    wrd_list = []

    for i, (char_images, char_heights) in enumerate(zip(word_images, word_heights)):
        avg_height = np.mean(char_heights) if char_heights else 0
        print(avg_height)

        if not char_images:
            wrd_list.append([])
            continue
        
        X_test = np.array(char_images)
        predictions = model.predict(X_test)
        confidences = [np.max(pred) for pred in predictions] 
        total_confidences.extend(confidences)  
        print([np.max(pred) for pred in predictions])

        #indices = [np.argmax(pred) for pred in predictions if np.max(pred) > 0.55]

        #predicted_labels = [labels[idx] for idx in indices] 
        indices = [i for i, pred in enumerate(predictions) if np.max(pred) > 0.45]

        predicted_labels = [labels[np.argmax(predictions[i])] for i in indices]
        print(predicted_labels)
        label_indices = [labels.index(label) for label in predicted_labels]
        print(label_indices)
        for j, idx in enumerate(indices): 
            if predicted_labels[j] == "ഠ" and char_heights[idx] < (0.8 * avg_height):
                predicted_labels[j] = "*"
            if char_heights[idx] < 24:
                predicted_labels[j] = '്'
            #elif char_heights[j] < 0.5 * avg_height:
                #predicted_labels[j] = "#" 
            if predicted_labels[j] in height_adjust_1 and char_heights[idx] < avg_height:
                predicted_labels[j] = 'ാ' 
            if predicted_labels[j] in height_adjust_2 and char_heights[idx] < (0.7 * avg_height):
                predicted_labels[j] = "*" 


        wrd_list.append(predicted_labels)
    if total_confidences:
        overall_confidence = np.mean(total_confidences) * 100  
        print(f"\n Overall Classification Confidence: {overall_confidence:.2f}% \n")
    else:
        print("\n No valid predictions found, overall confidence cannot be computed. \n")

    print("Classification completed successfully.")

    return wrd_list, overall_confidence

# classified_words = getLabels()
# print(classified_words)
