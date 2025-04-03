import cv2
import os
import numpy as np
import shutil

def segment(image_path):
    print("Segmenting...")

    if not os.path.exists(image_path):
        print("Error: Image file not found!")
        return

    inputfile = cv2.imread(image_path, 0)
    
    if inputfile is None:
        print("Error: Could not read the image.")
        return

    word_path = r"C:\Users\Irin\Downloads\final edit (2)\final edit\word"
    if os.path.exists(word_path):
        shutil.rmtree(word_path)

    os.mkdir(word_path)
    height_data = {}

    kernel = np.ones((6, 6), np.uint8)
    dilated_img = cv2.dilate(inputfile, kernel)

    denoised_img = cv2.fastNlMeansDenoising(dilated_img, None, 30, 7, 21)  
    bg_img = cv2.bilateralFilter(denoised_img, 15, 75, 75)  

    diff_img = 255 - cv2.absdiff(inputfile, bg_img)
    
    norm_img = cv2.normalize(diff_img, diff_img, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)
    shadow_removed_path = "shadow_removed.jpg"
    cv2.imwrite(shadow_removed_path, norm_img)

    gray = cv2.imread(shadow_removed_path, 0)
    blur = cv2.GaussianBlur(gray, (11, 11), 0)  

    _, line_binary = cv2.threshold(blur, 127, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    cv2.imwrite("binary_image.jpg", line_binary)

    line_binary = 255 - line_binary  
    word_count = 1

    line_kernel = np.ones((3, line_binary.shape[1] // 8), np.uint8)
    line_closed = cv2.morphologyEx(line_binary, cv2.MORPH_CLOSE, line_kernel)

    line_ctrs, _ = cv2.findContours(line_closed.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    line_sorted_ctrs = sorted(line_ctrs, key=lambda ctr: cv2.boundingRect(ctr)[1])

    if not os.path.exists("word"):
        os.mkdir("word")

    for line_ctr in line_sorted_ctrs:
        line_x, line_y, line_w, line_h = cv2.boundingRect(line_ctr)
        line_roi_binary = line_binary[line_y:line_y + line_h, line_x:line_x + line_w]

        word_kernel = np.ones((5, 25), np.uint8)
        word_dilated = cv2.dilate(line_roi_binary, word_kernel, iterations=2)
        word_closed = cv2.morphologyEx(word_dilated, cv2.MORPH_CLOSE, word_kernel)

        word_ctrs, _ = cv2.findContours(word_closed.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        word_sorted_ctrs = sorted(word_ctrs, key=lambda ctr: cv2.boundingRect(ctr)[0])

        for word_ctr in word_sorted_ctrs:
            word_x, word_y, word_w, word_h = cv2.boundingRect(word_ctr)
            word_roi = line_roi_binary[word_y:word_y + word_h, word_x:word_x + word_w]

            if word_roi.shape[1] > line_roi_binary.shape[1] // 50:
                word_dir = os.path.join("word", str(word_count))
                os.makedirs(word_dir, exist_ok=True)

                char_ctrs, _ = cv2.findContours(word_roi.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                min_area = 50  

                valid_contours = [cnt for cnt in char_ctrs if cv2.contourArea(cnt) > min_area]
                char_sorted_ctrs = sorted(valid_contours, key=lambda ctr: cv2.boundingRect(ctr)[0])
                #char_sorted_ctrs = sorted(char_ctrs, key=lambda ctr: cv2.boundingRect(ctr)[0])

                char_count = 1
                for char_ctr in char_sorted_ctrs:
                    char_x, char_y, char_w, char_h = cv2.boundingRect(char_ctr)
                    height_data[f"{word_count}_{char_count}"] = char_h 
                    char_roi_thresh = word_roi[char_y:char_y + char_h, char_x:char_x + char_w]

                    char_mask = np.zeros_like(word_roi)
                    cv2.drawContours(char_mask, [char_ctr], 0, (255, 255, 255), -1)
                    char_roi_mask = char_mask[char_y:char_y + char_h, char_x:char_x + char_w]
                    char_roi_thresh = cv2.bitwise_and(char_roi_thresh, char_roi_mask)
                    char_roi_thresh = 255 - char_roi_thresh

                    h, w = char_roi_thresh.shape
                    for _ in range(4):
                        base_size = (h + 20, w + 20)
                        base = np.zeros(base_size, dtype=np.uint8)
                        cv2.rectangle(base, (0, 0), (w + 20, h + 20), (255, 255, 255), 30)
                        base[10:h + 10, 10:w + 10] = char_roi_thresh
                        char_roi_thresh = base
                        h += 20
                        w += 20
                    
                    resized = cv2.resize(char_roi_thresh, (86, 86), interpolation=cv2.INTER_CUBIC)
                    cv2.imwrite(os.path.join(word_dir, f"{char_count}.jpg"), resized)
                    char_count += 1
                
                word_count += 1
    with open("char_heights.txt", "w") as f:
        for key, value in height_data.items():
            f.write(f"{key},{value}\n")
    print("Segmentation completed successfully!")
