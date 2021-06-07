import json
import itertools
import time

with open("armor_parts_per_skill.json") as json_data:
    skills_data = json.loads(json_data.read())

with open("armor_sets.json") as json_data:
    armor_sets_data = json.loads(json_data.read())


def calculate_part_skill_value(armor_set, armor_type, skill_list):

    armor_part = armor_sets_data.get(armor_set).get(armor_type)
    skill_value = 0
    for skill in armor_part.get("skills"):
        if skill.get("name") in skill_list: #and skills_data.get(skill.get("name")).get("slot_level") != "gem_level_1":
            skill_value += int(skill.get("value"))
    skills_gem_levels = sorted([int(skills_data.get(skill_name).get("slot_level").replace("gem_level_", "")) for skill_name in skill_list if skills_data.get(skill_name).get("slot_level") != '--'], reverse=True)
    counter = 0
    available_slots = len(armor_part.get("slots"))
    armor_part_slots = [slot_level for slot_level in armor_part.get("slots")]
    while available_slots > 0 and counter <= len(skills_gem_levels):
        for gem_level in skills_gem_levels:
            for i in range(0, available_slots):
                if int(armor_part_slots[i].replace("gem_level_", "")) >= gem_level:
                    del(armor_part_slots[i])
                    if gem_level > 1:
                        skill_value += 1
                    available_slots -= 1
                    break
            counter += 1
            if available_slots == 0:
                break
    return skill_value, armor_part


def sort_candidates_by_skill_value(my_armor_set_candidates):
    for part in my_armor_set_candidates:
        my_armor_set_candidates[part] = sorted(my_armor_set_candidates[part], key=lambda k: k['skill_value'], reverse=True)
    return my_armor_set_candidates


def calculate_skill_bonuses(armor_piece, my_build):
    bonuses_applied = []
    bonuses = dict()
    armor_piece = armor_piece.get("armor_piece")
    for skill in armor_piece.get("skills"):
        skill_name = skill.get("name")
        if skill_name in my_build.get("current_skill_levels"):
            new_skill_level = int(skill.get("value")) + my_build.get("current_skill_levels").get(skill_name)
            if not(new_skill_level > int(skills_data.get(skill_name).get("max_level"))):
                bonuses[skill_name] = new_skill_level
                bonuses_applied.append(True)
            else:
                bonuses_applied.append(False)
    if False not in bonuses_applied:
        for skill in bonuses:
            my_build.get("current_skill_levels")[skill] = bonuses.get(skill)
        return True
    else:
        return False


def is_skill_maxed_out(my_build, skill_name):
    if my_build.get("current_skill_levels").get(skill_name) == int(skills_data.get(skill_name).get("max_level")):
        return True
    else:
        return False


def get_skill_gem_level(skill_name):
    return skills_data.get(skill_name).get("slot_level")


def create_armor_set_candidates(my_skills):

    my_armor_set_candidates = {
        "Helm": [],
        "Chest": [],
        "Waist": [],
        "Arms": [],
        "Legs": []
    }
    for armor_set in armor_sets_data:
        for part in my_armor_set_candidates:
            skill_value, armor_piece = calculate_part_skill_value(armor_set, part, my_skills)
            if skill_value >= 2:
                candidate = {"armor_piece": armor_piece, "skill_value": skill_value}
                my_armor_set_candidates[armor_piece.get("type")].append(candidate)
        my_armor_set_candidates = sort_candidates_by_skill_value(my_armor_set_candidates)
    '''
    with open('armor_parts_candidates.json', 'w') as fp:
        json.dump(my_armor_set_candidates, fp)
    '''
    return my_armor_set_candidates


def get_slot_availability(gem_slots):
    slots_availability = {
        "gem_level_1": 0,
        "gem_level_2": 0,
        "gem_level_3": 0
    }
    for gem in gem_slots:
        slots_availability[gem] += 1

    return slots_availability


def insert_skill_in_slot(skill, build):
    if skill in build.get("current_skill_levels"):
        build.get("current_skill_levels")[skill] += 1
    else:
        build.get("current_skill_levels")[skill] = 1


def fill_gem_level_3_skills(slots_availability, build, my_skills):
    skills = [skill for skill in my_skills if get_skill_gem_level(skill) == "gem_level_3"]
    for skill in skills:
        while slots_availability.get("gem_level_3") > 0 and not is_skill_maxed_out(build, skill):
            insert_skill_in_slot(skill, build)
            slots_availability["gem_level_3"] -= 1
            build.get("skills_in_gem_slots")["level_3_slots"].append(skill)


def fill_gem_level_2_skills(slots_availability, build, my_skills):
    skills = [skill for skill in my_skills if get_skill_gem_level(skill) == "gem_level_2"]
    for skill in skills:
        while slots_availability.get("gem_level_3") > 0 and not is_skill_maxed_out(build, skill):
            insert_skill_in_slot(skill, build)
            slots_availability["gem_level_3"] -= 1
            build.get("skills_in_gem_slots")["level_3_slots"].append(skill)
        while slots_availability.get("gem_level_2") > 0 and not is_skill_maxed_out(build, skill):
            insert_skill_in_slot(skill, build)
            slots_availability["gem_level_2"] -= 1
            build.get("skills_in_gem_slots")["level_2_slots"].append(skill)


def fill_gem_level_1_skills(slots_availability, build, my_skills):
    skills = [skill for skill in my_skills if get_skill_gem_level(skill) == "gem_level_1"]
    for skill in skills:
        while slots_availability.get("gem_level_3") > 0 and not is_skill_maxed_out(build, skill):
            insert_skill_in_slot(skill, build)
            slots_availability["gem_level_3"] -= 1
            build.get("skills_in_gem_slots")["level_3_slots"].append(skill)
        while slots_availability.get("gem_level_2") > 0 and not is_skill_maxed_out(build, skill):
            insert_skill_in_slot(skill, build)
            slots_availability["gem_level_2"] -= 1
            build.get("skills_in_gem_slots")["level_2_slots"].append(skill)
        while slots_availability.get("gem_level_1") > 0 and not is_skill_maxed_out(build, skill):
            insert_skill_in_slot(skill, build)
            slots_availability["gem_level_1"] -= 1
            build.get("skills_in_gem_slots")["level_1_slots"].append(skill)


def calculate_build_skill_value(current_skill_levels, my_skills):
    total_skill_value = 0
    for skill, value in current_skill_levels.items():
        if skill in my_skills:
            total_skill_value += value
    return total_skill_value


def calculate_gem_level_3_value(current_skill_levels, my_skills):
    total_gem_level_3_value = 0
    for skill, value in current_skill_levels.items():
        if skill in my_skills and get_skill_gem_level(skill) == "gem_level_3":
            total_gem_level_3_value += value
    return total_gem_level_3_value


def calculate_gem_level_2_value(current_skill_levels, my_skills):
    total_gem_level_2_value = 0
    for skill, value in current_skill_levels.items():
        if skill in my_skills and get_skill_gem_level(skill) == "gem_level_2":
            total_gem_level_2_value += value
    return total_gem_level_2_value


def calculate_build_resistances(armor_parts):
    resistances = {
        "fire_resistance": 0,
        "water_resistance": 0,
        "thunder_resistance": 0,
        "ice_resistance": 0,
        "dragon_resistance": 0
    }

    for part in armor_parts:
        resistances["fire_resistance"] += int(part.get("fire_resistance"))
        resistances["water_resistance"] += int(part.get("water_resistance"))
        resistances["thunder_resistance"] += int(part.get("thunder_resistance"))
        resistances["ice_resistance"] += int(part.get("ice_resistance"))
        resistances["dragon_resistance"] += int(part.get("dragon_resistance"))

    total_resistances = sum([value for key, value in resistances.items()])
    return resistances, total_resistances


def calculate_build_defence(armor_parts):
    return sum([int(armor_part.get("defence")) for armor_part in armor_parts])


def calculate_build_stats(build_for_review, my_skills, talisman_skills, gem_list):
    build = {
        "armor_parts": [armor_piece.get("armor_piece") for armor_piece in build_for_review],
        #"item_names": [armor_piece.get("armor_piece").get("name") for armor_piece in build_for_review],
        "current_skill_levels": dict(),
        "gem_slots": [],
        "skills_in_gem_slots": {
            "level_3_slots": [],
            "level_2_slots": [],
            "level_1_slots": [],
        },
        "total_skill_value": 0,
        "skill_gem_level_3_value": 0,
        "skill_gem_level_2_value": 0
    }

    for skill in talisman_skills:
        if skill:
            for name, value in skill.items():
                build.get("current_skill_levels")[name] = value
                if name in my_skills:
                    build["total_skill_value"] += value

    build["gem_slots"].extend(gem_list)

    for armor_piece in build_for_review:
        item = armor_piece.get("armor_piece")
        for skill in item.get("skills"):
            skill_name = skill.get("name")
            try:
                skill_max_level = int(skills_data.get(skill_name).get("max_level"))
            except Exception as err:
                print(err)
                print(skill_name)
            if skill_name in build.get("current_skill_levels"):
                new_skill_level = build.get("current_skill_levels").get(skill_name) + int(skill.get("value"))
                if new_skill_level > skill_max_level:
                    build.get("current_skill_levels")[skill_name] = skill_max_level
                else:
                    build.get("current_skill_levels")[skill_name] = new_skill_level
            else:
                build.get("current_skill_levels")[skill_name] = int(skill.get("value"))
        build["gem_slots"].extend(item.get("slots"))
    #for reach skill in skill input that is not maxed out try and find an empty gem to fill it up with it
    slots_availability = get_slot_availability(build.get("gem_slots"))
    fill_gem_level_3_skills(slots_availability, build, my_skills)
    fill_gem_level_2_skills(slots_availability, build, my_skills)
    fill_gem_level_1_skills(slots_availability, build, my_skills)
    build["total_skill_value"] = calculate_build_skill_value(build.get("current_skill_levels"), my_skills)
    build["skill_gem_level_3_value"] = calculate_gem_level_3_value(build.get("current_skill_levels"), my_skills)
    build["skill_gem_level_2_value"] = calculate_gem_level_2_value(build.get("current_skill_levels"), my_skills)
    build["resistances"], build["total_resistances"] = calculate_build_resistances(build.get("armor_parts"))
    build["defence"] = calculate_build_defence(build.get("armor_parts"))
    return build


def build_generator_main(my_skills, talisman_skills, gem_list):
    starting_time = time.time()
    print(f"Creating armor set candidates starting at {starting_time}")
    my_armor_set_candidates = create_armor_set_candidates(my_skills)
    print(f"Finished creating armor set candidates, took {time.time() - starting_time} seconds.")
    starting_time = time.time()
    print(f"Starting combining armor set candidates at {starting_time}")
    build_combinations = list(itertools.product(*(my_armor_set_candidates[armor_part] for armor_part in my_armor_set_candidates)))
    print(f"Combinations length is :{len(build_combinations)}")
    print(f"Finished combining armor set candidates, took {time.time() - starting_time} seconds.")
    starting_time = time.time()
    print(f"Calculating top 100 builds, starting at {starting_time}")
    top_100_builds = sorted([calculate_build_stats(build, my_skills, talisman_skills, gem_list) for build in build_combinations], key=lambda k: k["total_skill_value"], reverse=True)[0:50]
    print(f"Finished calculating top 100 builds, took {time.time() - starting_time} seconds")
    top_10_sorted_by_level_3 = sorted(top_100_builds, key=lambda k: k["skill_gem_level_3_value"], reverse=True)[0:10]

    '''
    top_100_builds_dict = {
        "my_skills": str(my_skills),
        "my_top_50_builds": top_100_builds,
        "top_10_sorted_by_level_3_skills": top_10_sorted_by_level_3}

    
    with open("my_top_50_builds.json", 'w') as builds_creates:
        json.dump(top_100_builds_dict, builds_creates)
    '''
    return top_10_sorted_by_level_3


