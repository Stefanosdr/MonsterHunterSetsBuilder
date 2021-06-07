#NOTES: Need to add the previous build button
#Need to add the total resources for each build, that are required


from tkinter import *
from tkinter import messagebox
import json
from mh_build_generator import build_generator_main
import time

with open("armor_parts_per_skill.json") as json_data:
    skills_data = json.loads(json_data.read())

DEFAULT_NUMBER_OF_SKILLS = 10
SKILL_OPTIONS = sorted([skills_data.get(skill).get("name") for skill in skills_data])
GEM_LEVEL_DICT = {
            "Level 1 Gems": "gem_level_1",
            "Level 2 Gems": "gem_level_2",
            "Level 3 Gems": "gem_level_3"
        }

gem_levels = ["Level 1 Gems", "Level 2 Gems", "Level 3 Gems"]
build_number_to_display = 0

class SkillOption:

    def __init__(self, default_value, window):
        self.default_value = default_value
        self.skill_choice = StringVar()
        self.skill_choice.set(value=f"choose a skill")
        self.option_menu = OptionMenu(window, self.skill_choice, *SKILL_OPTIONS)
        self.option_menu.config(width=30, pady=10)
        self.skill_choice.trace_add("write", self.trace_skill_choice_value)
        self.option_menu.grid(row=default_value, column=0)
        self.skill_dict = None

    def trace_skill_choice_value(self, *args):
        print(f"The value of the variable is now {self.skill_choice.get()}")
        self.skill_level = IntVar()
        self.max_skill_value = int(skills_data.get(self.skill_choice.get()).get("max_level"))
        self.skill_level.set(value=self.max_skill_value)
        self.level_option = OptionMenu(window, self.skill_level, *[i for i in range(1, self.max_skill_value + 1)])
        self.level_option.config(width=30, pady=10, padx= 10)
        self.skill_level.trace_add("write", self.trace_skill_level_choice)
        self.level_option.grid(row=self.default_value, column=1)
        self.skill_dict = {self.skill_choice.get(): self.skill_level.get()}

    def trace_skill_level_choice(self, *args):
        self.skill_dict = {self.skill_choice.get(): self.skill_level.get()}


class GemOption:

    def __init__(self, gem_level, row_grid, column_grid, window,):

        self.gem_level = GEM_LEVEL_DICT.get(gem_level)
        self.row = row_grid
        self.column = column_grid
        self.gem_label = Label(window, text=self.gem_level)
        self.gem_label.config(font=("Courier", 10), width=30)
        self.gem_label.grid(row=self.row, column=self.column)
        self.gem_slots_var = IntVar()
        self.gem_slots_var.set(value=0)
        self.num_gem_option = OptionMenu(window, self.gem_slots_var, *[i for i in range(0, 4)])
        self.num_gem_option.config(width=30, pady=10)
        self.gem_slots_var.trace_add("write", self.trace_gem_choice_value)
        self.num_gem_option.grid(row=self.row, column=self.column + 1)
        self.gem_list = []

    def trace_gem_choice_value(self, *args):
        self.gem_list = [self.gem_level for i in range(0, self.gem_slots_var.get())]


window = Tk()
window.title('MH Armor Set Builder')
window.minsize(width=1000, height=1000)
window.config(padx=20, pady=20)



def clear_widgets():
    for widget in window.winfo_children():
        widget.destroy()


def generate_build(option_menus, talisman_skills, gems):
    input_data = list(set([option.skill_choice.get() for option in option_menus if
                    option.skill_choice.get() != "choose a skill"]))
    print(input_data)
    talisman_skill_list = [skill_option.skill_dict for skill_option in talisman_skills]
    gem_list = []
    for gem_option in gems:
        gem_list.extend(gem_option.gem_list)
    if len(input_data) >= 3:
        all_skills_level_1 = True
        for skill_name in input_data:
            if skills_data.get(skill_name).get("slot_level") in ["gem_level_2", "gem_level_3"]:
                all_skills_level_1 = False
                break
        if all_skills_level_1:
            messagebox.showwarning("Skills Level", "Please provide at least one level 2, or level 3 skill before "
                                   "submitting.")
        else:
            start_time = time.time()
            print("Generating Builds...")
            best_builds = build_generator_main(input_data, talisman_skill_list, gem_list)
            print(f"Generated requested builds. Time took{time.time() - start_time} seconds")
            clear_widgets()
            create_armor_set_page(best_builds)
    else:
        messagebox.showwarning("Number of Skills", "Please choose at least 3 skills before submitting.")



def create_landing_page():
    clear_widgets()

    option_menus = []
    talisman_skills = []
    talisman_gems = []
    weapon_gems = []
    gems = []

    skill_options_header = Label(window, text="Skill Choices")
    skill_options_header.config(font=("Courier", 20), width=30)
    skill_options_header.grid(row=0, column=0)

    skill_level_header = Label(window, text="Skill Level")
    skill_level_header.config(font=("Courier", 20), width=30)
    skill_level_header.grid(row=0, column=1)

    for i in range(0, 10):
        option_menus.append(SkillOption(i + 1, window))

    submit_skill_btn = Button(window, text="Submit Skills", command=lambda:generate_build(option_menus, talisman_skills, gems))
    submit_skill_btn.config(font=("Courier", 15), width=15)
    submit_skill_btn.grid(row=0, column=2)

    talisman_header = Label(window, text="Talisman Input")
    talisman_header.config(font=("Courier", 20), width=30, pady=10, padx=10)
    talisman_header.grid(row=len(option_menus) + 1, column=0)

    for i in range(len(option_menus) + 2, len(option_menus) + 4):
        talisman_skills.append(SkillOption(i, window))

    for i in range(0, len(gem_levels)):
        talisman_gems.append(GemOption(gem_levels[i], len(option_menus) + 4 + i, 0, window))

    weapon_gems_label = Label(window, text="Weapons Gem Slots")
    weapon_gems_label.config(font=("Courier", 20), width=30, pady=10, padx=10)
    weapon_gems_label.grid(row=len(option_menus) + 8)

    for i in range(0, len(gem_levels)):
        weapon_gems.append(GemOption(gem_levels[i], len(option_menus) + 9 + i, 0, window))

    gems = talisman_gems + weapon_gems


def create_armor_set_page(best_builds, number_to_display=0):
    print(best_builds)
    clear_widgets()
    global build_number_to_display
    build_number_to_display += 1
    if build_number_to_display >= len(best_builds):
        build_number_to_display = 0
    current_row = 0
    armor_parts_label = Label(window, text="Armor Parts")
    armor_parts_label.config(font=("Courier", 20), width=20, padx=10, pady=10)
    armor_parts_label.grid(row=current_row, column=0)
    current_row += 1
    build_to_display = best_builds[number_to_display]

    for armor_part in build_to_display.get("armor_parts"):
        armor_part_label = Label(window, text=f"{armor_part.get('name')}")
        armor_part_label.config(font=("Courier", 15), width=20, padx=5, pady=5)
        armor_part_label.grid(row=current_row, column=0)
        current_row += 1

    current_row = 0
    skill_values_label = Label(window, text="Skill Values")
    skill_values_label.config(font=("Courier", 20), width=20, padx=10, pady=10)
    skill_values_label.grid(row=current_row, column=1)
    current_row += 1

    for skill_name, value in build_to_display.get("current_skill_levels").items():
        skill_label = Label(window, text=f"{skill_name}: {value}")
        skill_label.config(font=("Courier", 15), width=30, padx=5, pady=5)
        skill_label.grid(row=current_row, column=1)
        current_row +=1
    total_gem_3_slots = 0
    total_gem_2_slots = 0
    total_gem_1_slots = 0
    for gem in build_to_display.get("gem_slots"):
        if gem == "gem_level_1":
            total_gem_1_slots += 1
        elif gem == "gem_level_2":
            total_gem_2_slots += 1
        else:
            total_gem_3_slots += 1
    total_gem_slots = [total_gem_3_slots, total_gem_2_slots, total_gem_1_slots]
    gem_pointer = 0
    current_row = 0
    for gem_level in build_to_display.get("skills_in_gem_slots"):
        gem_level_label = Label(window, text=f"{gem_level}({total_gem_slots[gem_pointer]})")
        gem_level_label.config(font=("Courier", 20), width=20, padx=10, pady=10)
        gem_level_label.grid(row=current_row, column=2)
        current_row += 1
        if len(build_to_display.get("skills_in_gem_slots").get(gem_level)) > 0:
            for skill in build_to_display.get("skills_in_gem_slots").get(gem_level):
                skill_in_gem_label = Label(window, text=skill)
                skill_in_gem_label.config(font=("Courier", 15), width=20, padx=5, pady=5)
                skill_in_gem_label.grid(row=current_row, column=2)
                current_row += 1
        else:
            empty_label = Label(window, text="--")
            empty_label.config(font=("Courier", 15), width=20, padx=5, pady=5)
            empty_label.grid(row=current_row, column=2)
            current_row += 1
        gem_pointer += 1

    resistances_label = Label(window, text="Resistances")
    resistances_label.config(font=("Courier", 20), width=20, padx=10, pady=10)
    resistances_label.grid(row=0, column=3)

    defence_label = Label(window, text=f"Defence: {build_to_display.get('defence')}")
    defence_label.config(font=("Courier", 15), width=20, padx=5, pady=5)
    defence_label.grid(row=1, column=3)

    current_row = 2

    for resistance, value in build_to_display.get("resistances").items():
        resistance_label = Label(window, text=f"{resistance}: {value}")
        resistance_label.config(font=("Courier", 15), width=20, padx=5, pady=5)
        resistance_label.grid(row=current_row, column=3)
        current_row += 1

    starting_page_btn = Button(window, text="Starting Page", command=create_landing_page)
    starting_page_btn.config(font=("Courier", 15), width=15, padx=10, pady=10)
    starting_page_btn.grid(row=30, column=0)

    next_build_btn = Button(window, text="Next Build", command= lambda: create_armor_set_page(best_builds, build_number_to_display))
    next_build_btn.config(font=("Courier", 15), width=15, padx=20, pady=10)
    next_build_btn.grid(row=30, column=1)


create_landing_page()
window.mainloop()


