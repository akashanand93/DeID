from utils.constants import DataConstants
import matplotlib.pyplot as plt
import json
import argparse
import tqdm
import numpy as np
import os




class Accuracy:
    def __init__(self, file_path, root_dir, dataset, trues=[], preds=[]):
        self.inp_file = file_path
        self.file_name = self.inp_file.split("/")[-1].split(".")[0]
        self.out_dir = DataConstants.METRICS_DIR.format(root_dir=root_dir)
        os.makedirs(self.out_dir, exist_ok=True)
        self.dataset = dataset
        self.trues = trues
        self.preds = preds

    def calculate_accuracy(self):
        tagged_sentences = []
        with open(self.inp_file, "r", encoding="utf-8") as file:
            for line in tqdm.tqdm(file):
                tagged_sentences.append(json.loads(line))
        
        match_ = 0
        total_ = 0
        correctly_tagged = 0
        incorrectly_tagged = 0
        untagged = 0
        extra_tagged = 0
        correctly_tagged_dict = {}
        incorrectly_tagged_dict = {}
        untagged_dict = {}
        extra_tagged_dict = {}
        mis_matched_tags = []
        if self.dataset == "2006":
            raw_categories = ['NAME', 'AGE', 'DATE', 'ID', 'LOCATION', 'HOSPITAL', 'DOCTOR', 'PHONE']
        elif self.dataset == "2014":
            raw_categories = ["NAME", "LOCATION", "AGE", "ID", "DATE", "CONTACT", "PROFESSION"]
        else:
            raw_categories = []
        categories = []
        for category in raw_categories:
            categories.append("B-" + category)
            categories.append("I-" + category)
        for category in categories:
            key_ = category[2:]
            correctly_tagged_dict[key_] = 0
            incorrectly_tagged_dict[key_] = 0
            untagged_dict[key_] = 0
            extra_tagged_dict[key_] = 0
        for sentence in tagged_sentences:
            mimic = []
            gpt = []
            total_ += len(sentence["annotations"]["annotations"])
            for annotation in sentence["annotations"]["annotations"]:
                for sannotation in sentence["secondary_annotations"]["annotations"]:
                    if sannotation["token"] == annotation["token"] and sannotation["start_index"] == annotation["start_index"]:
                        true = annotation["type"]
                        pred = sannotation["type"]
                        for category in categories:
                            key_ = category[2:]
                            if true == category and pred == category:
                                correctly_tagged_dict[key_] += 1
                                correctly_tagged += 1
                            elif true == category and pred == "NO_TYPE":
                                untagged_dict[key_] += 1
                                untagged += 1
                                mimic.append([annotation["start_index"], annotation["end_index"], annotation["type"]])
                                gpt.append([sannotation["start_index"], sannotation["end_index"], sannotation["type"]])
                            elif true == category and pred != category:
                                incorrectly_tagged_dict[key_] += 1
                                incorrectly_tagged += 1
                                mimic.append([annotation["start_index"], annotation["end_index"], annotation["type"]])
                                gpt.append([sannotation["start_index"], sannotation["end_index"], sannotation["type"]])
                            elif true == "NO_TYPE" and pred == category:
                                extra_tagged_dict[key_] += 1
                                extra_tagged += 1
                                mimic.append([annotation["start_index"], annotation["end_index"], annotation["type"]])
                                gpt.append([sannotation["start_index"], sannotation["end_index"], sannotation["type"]])
                        match_ += 1
                        break
            if len(gpt) or len(mimic):
                mis_matched_tags.append({
                    "text": sentence["text"] + "   __MIMIC",
                    "label": mimic  
                })
                mis_matched_tags.append({
                    "text": sentence["text"] + "   __GPT",
                    "label": gpt  
                })                             
        
        print(f"Matched {match_} out of {total_} tags : {round((match_ / total_) * 100, 2)}%")
        print("Correctly tagged: ", correctly_tagged)
        print("Incorrectly tagged: ", incorrectly_tagged)
        print("Untagged: ", untagged)
        print("Extra tagged: ", extra_tagged)
        print("Correctly tagged: ", correctly_tagged_dict)
        print("Incorrectly tagged: ", incorrectly_tagged_dict)
        print("Untagged: ", untagged_dict)
        print("Extra tagged: ", extra_tagged_dict)
        sum = correctly_tagged + incorrectly_tagged + untagged
        metrics = {
            "correctly_tagged(%)": round((correctly_tagged / sum) * 100, 2),
            "incorrectly_tagged(%)": round((incorrectly_tagged / sum) * 100, 2),
            "untagged(%)": round((untagged / sum) * 100, 2),
            "extra_tagged(%)": round((extra_tagged / match_) * 100, 2),
        }
        print(metrics)
        
        categories = raw_categories
        fig = plt.figure(figsize=(8,6))
        fig = plt.figure(facecolor=(1, 1, 1))
        ax = fig.add_axes([0,0,1,1])
        bottom = np.zeros(len(categories))
        p = ax.bar(categories, [correctly_tagged_dict[category] for category in categories], color='g', width=0.6, label="Correctly Tagged", bottom=bottom)
        bottom += np.array([correctly_tagged_dict[category] for category in categories])
        ax.bar_label(p,label_type="center")
        p = ax.bar(categories, [incorrectly_tagged_dict[category] for category in categories], color='b', width=0.6, label="Incorrectly Tagged", bottom=bottom)
        bottom += np.array([incorrectly_tagged_dict[category] for category in categories])
        ax.bar_label(p, label_type="center")
        p = ax.bar(categories, [untagged_dict[category] for category in categories], color='r', width=0.6, label="Untagged", bottom=bottom)
        bottom += np.array([untagged_dict[category] for category in categories])
        ax.bar_label(p, label_type="center")
        p = ax.bar(categories, [extra_tagged_dict[category] for category in categories], color='y', width=0.6, label="Extra Tagged", bottom=bottom)
        ax.bar_label(p, label_type="center")
        ax.legend()
        fig.savefig(f"{self.out_dir}/{self.file_name}-BarPlot.jpg", bbox_inches='tight')
        with open(f"{self.out_dir}/{self.file_name}-mismatches.json", "w") as f:
            for tag in mis_matched_tags:
                f.write(json.dumps(tag) + "\n")


def main(args):
    accuracy = Accuracy(args.input_file, args.root_dir, args.dataset)
    accuracy.calculate_accuracy()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a accuracy report.")
    parser.add_argument(
        "-i", "--input_file", type=str, help="Path to the input data file"
    )
    parser.add_argument(
        "-r", "--root_dir", type=str, help="Root directory to store metrics"
    )
    parser.add_argument(
        "-d", "--dataset", type=str, help="Root directory to store metrics"
    )
    args = parser.parse_args()
    main(args)
