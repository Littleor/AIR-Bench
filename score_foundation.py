import argparse
import json
from collections import defaultdict

from utils.logger_config import (
    print_detailed_results,
    print_results_table,
    setup_logger,
)


def parse_args():
    parser = argparse.ArgumentParser(description="Score foundation model results")
    parser.add_argument(
        "input_file",
        type=str,
        default="logs/Foundation_result_modelx.jsonl",
        help="Input file path (default: Foundation_result_modelx.jsonl)",
    )
    return parser.parse_args()


def get_category_mapping():
    return {
        "Speech_Grounding": "Speech grounding",
        "Spoken_Language_Identification": "Spoken language identification",
        "Speaker_Gender_Recognition": "Speaker gender recognition",
        "Speaker_Emotion_Recontion": "Emotion recognition",
        "Speaker_Age_Prediction": "Speaker age prediction",
        "Speech_Entity_Reconition": "Speech entity recognition",
        "Speaker_Intent_Classification": "Intent classification",
        "Speaker_Number_Verification": "Speaker number verification",
        "Synthesized_Voice_Detection": "Synthesized voice detection",
        "Audio_Grounding": "Audio grounding",
        "vocal_sound_classification": "Vocal sound classification",
        "Acoustic_Scene_Classification": "Acoustic scene classification",
        "Sound_AQA": "Sound question answering",
        "Music_Instruments_Classfication": "Music instruments classification",
        "Music_Genre_Recognition": "Music genre classfication",
        "Music_Midi_Pitch_Analysis": "Music note analysis-pitch",
        "Music_Midi_Velocity_Analysis": "Music note analysis-velocity",
        "Music_AQA": "Music question answering",
        "Music_Mood_Recognition": "Music emotion detection",
    }


def main():
    args = parse_args()
    input_file = args.input_file
    logger = setup_logger("score_foundation")

    fail_num = 0
    task_id_list = []
    total_num_dict = {}
    correct_num_dict = {}
    category_mapping = get_category_mapping()

    with open(input_file, "r") as fp:
        for data in fp:
            line = json.loads(data)
            task_name = line["task_name"]
            dataset_name = line["dataset_name"]
            if task_name == None:
                print("1.task_name is None")
                continue
            task_id = task_name + "_" + dataset_name
            if task_id not in task_id_list:
                task_id_list.append(task_id)
            total_num = total_num_dict.get(task_id, 0)
            correct_num = correct_num_dict.get(task_id, 0)
            predict = line["response"].strip().replace("\n", "")
            if predict != "None" and predict:
                if (
                    predict[0] == "A"
                    or predict[0] == "B"
                    or predict[0] == "C"
                    or predict[0] == "D"
                ):
                    gpt_predict = predict[0]
                    if line["answer_gt"] == line["choice_a"]:
                        gt = "A"
                    elif line["answer_gt"] == line["choice_b"]:
                        gt = "B"
                    elif line["answer_gt"] == line.get("choice_c", None):
                        gt = "C"
                    elif line["answer_gt"] == line.get("choice_d", None):
                        gt = "D"
                    else:
                        print("???? gt_answer is: ", end="")
                        print(line["answer_gt"])
                        exit(1)
                # This situation may occur when the answer given by gpt is "The answer is A."
                elif len(predict) > 1:
                    if (
                        predict[-2] == "A"
                        or predict[-2] == "B"
                        or predict[-2] == "C"
                        or predict[-2] == "D"
                    ):
                        gpt_predict = predict[-2]
                        if line["answer_gt"] == line["choice_a"]:
                            gt = "A"
                        elif line["answer_gt"] == line["choice_b"]:
                            gt = "B"
                        elif line["answer_gt"] == line.get("choice_c", None):
                            gt = "C"
                        elif line["answer_gt"] == line.get("choice_d", None):
                            gt = "D"
                        else:
                            print("???? gt_answer is: ", end="")
                            print(line["answer_gt"])
                            exit(1)
                    else:
                        print(f"response is {predict}")
                        fail_num += 1
                        continue
                else:
                    print(f"response is {predict}")
                    fail_num += 1
                    continue

                if gt == gpt_predict:
                    total_num += 1
                    correct_num += 1
                else:
                    total_num += 1

                total_num_dict[task_id] = total_num
                correct_num_dict[task_id] = correct_num

            else:
                print("2.Response is None.")
                fail_num += 1

    total_sum = 0
    task_results = []
    for task_id in task_id_list:
        total_num = total_num_dict[task_id]
        correct_num = correct_num_dict[task_id]
        acc = correct_num / total_num
        total_sum += total_num
        task_results.append(
            {"task_id": task_id, "total": total_num, "correct": correct_num, "acc": acc}
        )

    category_stats = defaultdict(lambda: {"total": 0, "correct": 0})

    for task_id in task_id_list:
        base_task = task_id.split("_")[0]
        find_flag = False
        for key in category_mapping.keys():
            if task_id.startswith(key):
                category_stats[category_mapping[key]]["total"] += total_num_dict[
                    task_id
                ]
                category_stats[category_mapping[key]]["correct"] += correct_num_dict[
                    task_id
                ]
                find_flag = True
                break
        if not find_flag:
            raise ValueError(f"Warning: Task {task_id} not mapped to any category")

    # print_header(logger, "Detailed Task Results")
    print_detailed_results(logger, task_results)

    logger.info(f"[bold blue]Total samples:[/bold blue] {total_sum}")
    logger.info(f"[bold red]Failed samples:[/bold red] {fail_num}")

    # print_header(logger, "Category-wise Results")
    print_results_table(logger, category_stats)


if __name__ == "__main__":
    main()
