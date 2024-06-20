from models.model import SingleAnnotation, UserInfo2006i2b2, UserInfo2014i2b2
from typing import List
import json
from loguru import logger


def convert_human_readable_to_machine_readable_annotations(
    sentence: str, tags: List[SingleAnnotation]
) -> List[SingleAnnotation]:
    tags = sorted(tags, key=lambda x: x.start_index)
    annotations = []
    sent = sentence
    sent1 = sentence
    for tag in tags:
        token = [t for t in tag.token.split(" ") if len(t) > 0]
        for i in range(len(token)):
            start = sentence.find(token[i])
            end = sentence.find(token[i]) + len(token[i])
            annotations.append(
                SingleAnnotation(
                    token=token[i],
                    start_index=start,
                    end_index=end,
                    type=f"B-{tag.type}" if i == 0 else f"I-{tag.type}",
                )
            )
            for j in range(0, end):
                sentence = sentence.replace(sentence[j], "{", 1)
            sent = sent[:start] + "{" * len(token[i]) + sent[end:]
            sent1 = sent1[:start] + " " * len(token[i]) + sent1[end:]
    sent1 = [s for s in sent1.strip().split(" ") if len(s) > 0]
    for s in sent1:
        annotations.append(
            SingleAnnotation(
                token=s,
                start_index=sent.index(s),
                end_index=sent.index(s) + len(s),
                type="NO_TYPE",
            )
        )
        sent = sent.replace(s, "{" * len(s), 1)
    annotations = sorted(annotations, key=lambda x: x.start_index)
    return annotations


def convert_machine_readable_to_human_readable_annotations(
    sentence: str, tags: List[SingleAnnotation]
) -> List[SingleAnnotation]:
    annotations = []
    for i in range(len(tags)):
        if tags[i].type == "NO_TYPE":
            continue
        else:
            if tags[i].type[0] == "B":
                entity = tags[i].type[2:]
                start = tags[i].start_index
                end = tags[i].end_index
                for j in range(i + 1, len(tags)):
                    if tags[j].type == "I-" + entity:
                        end = tags[j].end_index
                    else:
                        break
                annotations.append(
                    SingleAnnotation(
                        token=sentence[start:end],
                        start_index=start,
                        end_index=end,
                        type=entity,
                    )
                )
    annotations = sorted(annotations, key=lambda x: x.start_index)
    return annotations


def convert_human_readable_to_doccano_annotations_in_ndjson(
    sentence: str, tags: List[SingleAnnotation], _tag_source: str, id: str
) -> dict:
    annotations = {"text": sentence + f"    {_tag_source}_{id}", "label": []}
    for tag in tags:
        annotations["label"].append([tag.start_index, tag.end_index, tag.type])
    return annotations


def write_doccano_tagged_sentences(
    sentences1: List[dict],
    file_path: str,
    file_name: str,
    _type: str = "ndjson",
    sentences2: List[dict] = [],
) -> None:
    if _type != "ndjson":
        raise ValueError("Only 'ndjson' type is supported")
    with open(f"{file_path}/{file_name}.{_type}", "w") as f:
        for i in range(len(sentences1)):
            f.write(json.dumps(sentences1[i]) + "\n")
            if len(sentences2):
                f.write(json.dumps(sentences2[i]) + "\n")
    logger.success(
        f"Loaded {len(sentences1)+len(sentences2)} to file {file_path}/{file_name}.{_type}"
    )
    return


def get_human_readable_annotations_2006i2b2(
    sentence: str, response_obj: UserInfo2006i2b2
) -> List[SingleAnnotation]:
    annotations = []
    for i in range(len(response_obj.patients)):
        while response_obj.patients[i] in sentence:
            annotations.append(
                SingleAnnotation(
                    token=response_obj.patients[i],
                    start_index=sentence.index(response_obj.patients[i]),
                    end_index=sentence.index(response_obj.patients[i])
                    + len(response_obj.patients[i]),
                    type="PATIENT",
                )
            )
            sentence = sentence.replace(
                response_obj.patients[i], "{" * len(response_obj.patients[i]), 1
            )
    for i in range(len(response_obj.doctors)):
        while response_obj.doctors[i] in sentence:
            annotations.append(
                SingleAnnotation(
                    token=response_obj.doctors[i],
                    start_index=sentence.index(response_obj.doctors[i]),
                    end_index=sentence.index(response_obj.doctors[i])
                    + len(response_obj.doctors[i]),
                    type="DOCTOR",
                )
            )
            sentence = sentence.replace(
                response_obj.doctors[i], "{" * len(response_obj.doctors[i]), 1
            )
    for i in range(len(response_obj.hospitals)):
        while response_obj.hospitals[i] in sentence:
            annotations.append(
                SingleAnnotation(
                    token=response_obj.hospitals[i],
                    start_index=sentence.index(response_obj.hospitals[i]),
                    end_index=sentence.index(response_obj.hospitals[i])
                    + len(response_obj.hospitals[i]),
                    type="HOSPITAL",
                )
            )
            sentence = sentence.replace(
                response_obj.hospitals[i], "{" * len(response_obj.hospitals[i]), 1
            )
    for i in range(len(response_obj.ids)):
        while response_obj.ids[i] in sentence:
            annotations.append(
                SingleAnnotation(
                    token=response_obj.ids[i],
                    start_index=sentence.index(response_obj.ids[i]),
                    end_index=sentence.index(response_obj.ids[i])
                    + len(response_obj.ids[i]),
                    type="ID",
                )
            )
            sentence = sentence.replace(
                response_obj.ids[i], "{" * len(response_obj.ids[i]), 1
            )
    for i in range(len(response_obj.dates)):
        while response_obj.dates[i] in sentence:
            annotations.append(
                SingleAnnotation(
                    token=response_obj.dates[i],
                    start_index=sentence.index(response_obj.dates[i]),
                    end_index=sentence.index(response_obj.dates[i])
                    + len(response_obj.dates[i]),
                    type="DATE",
                )
            )
            sentence = sentence.replace(
                response_obj.dates[i], "{" * len(response_obj.dates[i]), 1
            )
    for i in range(len(response_obj.locations)):
        while response_obj.locations[i] in sentence:
            annotations.append(
                SingleAnnotation(
                    token=response_obj.locations[i],
                    start_index=sentence.index(response_obj.locations[i]),
                    end_index=sentence.index(response_obj.locations[i])
                    + len(response_obj.locations[i]),
                    type="LOCATION",
                )
            )
            sentence = sentence.replace(
                response_obj.locations[i], "{" * len(response_obj.locations[i]), 1
            )
    for i in range(len(response_obj.phone_numbers)):
        while response_obj.phone_numbers[i] in sentence:
            annotations.append(
                SingleAnnotation(
                    token=response_obj.phone_numbers[i],
                    start_index=sentence.index(response_obj.phone_numbers[i]),
                    end_index=sentence.index(response_obj.phone_numbers[i])
                    + len(response_obj.phone_numbers[i]),
                    type="PHONE",
                )
            )
            sentence = sentence.replace(
                response_obj.phone_numbers[i],
                "{" * len(response_obj.phone_numbers[i]),
                1,
            )
    for i in range(len(response_obj.ages)):
        while response_obj.ages[i] in sentence:
            age = "".join([a for a in response_obj.ages[i] if a.isnumeric()])
            if age and int(age) > 90:
                annotations.append(
                    SingleAnnotation(
                        token=age,
                        start_index=sentence.index(age),
                        end_index=sentence.index(age) + len(age),
                        type="AGE",
                    )
                )
                sentence = sentence.replace(age, "{" * len(age), 1)
            else:
                break
    annotations = sorted(annotations, key=lambda x: x.start_index)
    return annotations


def get_human_readable_annotations_2014i2b2(
    sentence: str, response_obj: UserInfo2014i2b2
) -> List[SingleAnnotation]:
    annotations = []
    for i in range(len(response_obj.names)):
        while response_obj.names[i] in sentence:
            annotations.append(
                SingleAnnotation(
                    token=response_obj.names[i],
                    start_index=sentence.index(response_obj.names[i]),
                    end_index=sentence.index(response_obj.names[i])
                    + len(response_obj.names[i]),
                    type="NAME",
                )
            )
            sentence = sentence.replace(
                response_obj.names[i], "{" * len(response_obj.names[i]), 1
            )
    for i in range(len(response_obj.locations)):
        while response_obj.locations[i] in sentence:
            annotations.append(
                SingleAnnotation(
                    token=response_obj.locations[i],
                    start_index=sentence.index(response_obj.locations[i]),
                    end_index=sentence.index(response_obj.locations[i])
                    + len(response_obj.locations[i]),
                    type="LOCATION",
                )
            )
            sentence = sentence.replace(
                response_obj.locations[i], "{" * len(response_obj.locations[i]), 1
            )
    for i in range(len(response_obj.ages)):
        while response_obj.ages[i] in sentence:
            annotations.append(
                SingleAnnotation(
                    token=response_obj.ages[i],
                    start_index=sentence.index(response_obj.ages[i]),
                    end_index=sentence.index(response_obj.ages[i])
                    + len(response_obj.ages[i]),
                    type="AGE",
                )
            )
            sentence = sentence.replace(
                response_obj.ages[i], "{" * len(response_obj.ages[i]), 1
            )
    for i in range(len(response_obj.ids)):
        while response_obj.ids[i] in sentence:
            annotations.append(
                SingleAnnotation(
                    token=response_obj.ids[i],
                    start_index=sentence.index(response_obj.ids[i]),
                    end_index=sentence.index(response_obj.ids[i])
                    + len(response_obj.ids[i]),
                    type="ID",
                )
            )
            sentence = sentence.replace(
                response_obj.ids[i], "{" * len(response_obj.ids[i]), 1
            )
    for i in range(len(response_obj.dates)):
        while response_obj.dates[i] in sentence:
            annotations.append(
                SingleAnnotation(
                    token=response_obj.dates[i],
                    start_index=sentence.index(response_obj.dates[i]),
                    end_index=sentence.index(response_obj.dates[i])
                    + len(response_obj.dates[i]),
                    type="DATE",
                )
            )
            sentence = sentence.replace(
                response_obj.dates[i], "{" * len(response_obj.dates[i]), 1
            )
    for i in range(len(response_obj.contacts)):
        while response_obj.contacts[i] in sentence:
            annotations.append(
                SingleAnnotation(
                    token=response_obj.contacts[i],
                    start_index=sentence.index(response_obj.contacts[i]),
                    end_index=sentence.index(response_obj.contacts[i])
                    + len(response_obj.contacts[i]),
                    type="CONTACT",
                )
            )
            sentence = sentence.replace(
                response_obj.contacts[i], "{" * len(response_obj.contacts[i]), 1
            )
    for i in range(len(response_obj.professions)):
        while response_obj.professions[i] in sentence:
            annotations.append(
                SingleAnnotation(
                    token=response_obj.professions[i],
                    start_index=sentence.index(response_obj.professions[i]),
                    end_index=sentence.index(response_obj.professions[i])
                    + len(response_obj.professions[i]),
                    type="PROFESSION",
                )
            )
            sentence = sentence.replace(
                response_obj.professions[i],
                "{" * len(response_obj.professions[i]),
                1,
            )
    annotations = sorted(annotations, key=lambda x: x.start_index)
    return annotations