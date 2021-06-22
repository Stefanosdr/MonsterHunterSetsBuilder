

from tkinter import *
from tkinter import messagebox
import json
from mh_build_generator import build_generator_main
import time

with open("armor_parts_per_skill.json") as json_data:
    skills_data = json.loads(json_data.read())

with open("armor_sets.json") as json_data2:
    armor_sets_data = json.loads(json_data2.read())

DEFAULT_NUMBER_OF_SKILLS = 10
SKILL_OPTIONS = sorted([skills_data.get(skill).get("name") for skill in skills_data])
GEM_LEVEL_DICT = {
            "Level 1 Gems": "gem_level_1",
            "Level 2 Gems": "gem_level_2",
            "Level 3 Gems": "gem_level_3"
        }

gem_levels = ["Level 1 Gems", "Level 2 Gems", "Level 3 Gems"]
ARMOR_PART_POS = ["Helm", "Chest", "Arms", "Waist", "Legs"]
build_number_to_display = 0
armor_parts_option_menus = []
item_preview_labels = []



def track_build_changes(armor_parts_option_menus, build_preview_obj):
    armor_parts_data = [armor_part_option.get_armor_part_data() for armor_part_option in armor_parts_option_menus]
    build_preview_obj.update_build_data(armor_parts_data)


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
        self.skill_level_option = OptionMenu(window, self.skill_level, *SKILL_OPTIONS)
        self.skill_level_option.config(width=30, pady=10)
        self.skill_level_option.grid(row=self.default_value, column=1)
        self.skill_level.trace_add("write", self.trace_skill_level_choice)
        self.skill_dict = {self.skill_choice.get(): self.skill_level.get()}


    def trace_skill_level_choice(self, *args):
        self.skill_dict = {self.skill_choice.get(): self.skill_level.get()}


class GemOption:

    def __init__(self, gem_level, row_grid, column_grid, window):

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


class ArmorPartOption:

    def __init__(self, row_grid, column_grid, part_type, window, build_preview_input):
        self.build_preview = build_preview_input
        self.window = window
        self.row = row_grid
        self.column = column_grid
        self.part_type = part_type
        self.skills_to_filter = []
        self.gems_to_filter = []
        self.reset_filters = False
        self.part_choice = StringVar()
        self.part_choice.set(value=self.part_type)
        self.part_choice.trace_add("write", self.armor_part_preview)
        self.armor_part_data = None
        self.latest_skill_to_filter = StringVar()
        self.latest_skill_to_filter.set(value="skill choice")
        self.part_choice.set(value=f"{part_type} Choice")
        self.set_default_choices()
        print(type(self.part_type_choices))
        self.part_option_menu = OptionMenu(self.window, self.part_choice, *self.part_type_choices)
        self.part_option_menu.config(font=("Courier", 10), padx=5, pady=5, width=25)
        self.part_option_menu.grid(row=self.row, column=self.column, sticky="W")

    def update_available_options(self):
        self.part_type_choices.clear()
        for armor_set in armor_sets_data:
            armor_part_name = armor_sets_data.get(armor_set).get(self.part_type).get("name")
            if "No " not in armor_part_name:
                armor_part_skills = set([skill_dict.get("name") for skill_dict in
                                         armor_sets_data.get(armor_set).get(self.part_type).get("skills")])
                armor_part_slots = set(armor_sets_data.get(armor_set).get(self.part_type).get("slots"))
                if set(self.skills_to_filter).issubset(armor_part_skills) and set(self.gems_to_filter).issubset(armor_part_slots):
                    self.part_type_choices.append(armor_part_name)
        if len(self.part_type_choices) == 0:
            self.part_type_choices.append("Empty")
        self.part_option_menu.forget()
        self.render_option_menu()

    def update_available_options_on_skills(self, filtered_skills):
        self.skills_to_filter = filtered_skills
        self.update_available_options()

    def update_available_options_on_gems(self, gems_dict):
        self.gems_to_filter = [gem_level for gem_level in gems_dict if gems_dict.get(gem_level).get()]
        self.update_available_options()

    def set_default_choices(self):
        self.part_type_choices = [armor_sets_data.get(armor_set).get(self.part_type).get("name") for armor_set in armor_sets_data if
                                  armor_sets_data.get(armor_set).get(self.part_type).get("name") != "No "+self.part_type]

    def render_option_menu(self):
        previous_value = self.part_choice.get()
        self.part_choice = StringVar()
        self.part_choice.set(value=previous_value)
        self.part_choice.trace_add("write", self.armor_part_preview)

        self.part_option_menu = OptionMenu(self.window, self.part_choice, *self.part_type_choices)
        self.part_option_menu.config(font=("Courier", 10), padx=5, pady=5, width=25)
        self.part_option_menu.grid(row=self.row, column=self.column, sticky="W")

    def get_armor_part_data(self):
        armor_part_data = None
        for armor_set in armor_sets_data:
            if self.part_choice.get() == armor_sets_data.get(armor_set).get(self.part_type).get("name"):
                armor_part_data = armor_sets_data.get(armor_set).get(self.part_type)
        return armor_part_data

    def armor_part_preview(self, *args):
        if item_preview_labels:
            for item_preview_label in item_preview_labels:
                item_preview_label.destroy()
        current_row_label = 7
        if self.part_choice != "Empty":
            print(f"User Choice: {self.part_choice}")
            self.armor_part_data = self.get_armor_part_data()

        for key, value in self.armor_part_data.items():
            if key == "slots":
                gems = {
                    "Level 1 Gems": value.count("gem_level_1"),
                    "Level 2 Gems": value.count("gem_level_2"),
                    "Level 3 Gems": value.count("gem_level_3")
                }
                for level, amount in gems.items():
                    preview_label = Label(self.window, text=f"{level}:{amount}")
                    preview_label.config(font=("Courier", 10), padx=5, pady=5, width=25)
                    preview_label.grid(row=current_row_label, column=0, sticky="W")
                    item_preview_labels.append(preview_label)
                    current_row_label += 1
            elif key == "skills":
                for skill_dict in value:
                    preview_label = Label(self.window, text=f"{skill_dict.get('name')}:{skill_dict.get('value')}")
                    preview_label.config(font=("Courier", 10), padx=5, pady=5, width=25)
                    preview_label.grid(row=current_row_label, column=0, sticky="W")
                    item_preview_labels.append(preview_label)
                    current_row_label += 1
            else:
                preview_label = Label(self.window, text=f"{key}:{value}")
                preview_label.config(font=("Courier", 10), padx=5, pady=5, width=25)
                preview_label.grid(row=current_row_label, column=0, sticky="W")
                item_preview_labels.append(preview_label)
                current_row_label += 1

        #We need to run something here that knows about option_menu_list and build preview
        track_build_changes(armor_parts_option_menus, self.build_preview)


class BuildPreview:

    def __init__(self, window):
        self.window = window
        self.build_preview_labels = []
        self.build_skills = dict()
        self.build_gem_slots = {
            "Level 1": 0,
            "Level 2": 0,
            "Level 3": 0
        }
        self.build_resistances = {
            "Defence": 0,
            "Fire Resistance": 0,
            "Water Resistance": 0,
            "Thunder Resistance": 0,
            "Ice Resistance": 0,
            "Dragon Resistance": 0
        }

    def render_build_skills(self):
        current_row = 8
        for skill, value in self.build_skills.items():
            skill_label = Label(self.window, text=f"{skill}:{value}")
            skill_label.config(font=("Courier", 10), padx=5, pady=5, width=20)
            skill_label.grid(row=current_row, column=1)
            current_row += 1
            self.build_preview_labels.append(skill_label)

    def render_build_gem_slots(self):
        current_row = 8
        for gem, value in self.build_gem_slots.items():
            gem_label = Label(self.window, text=f"{gem}:{value}")
            gem_label.config(font=("Courier", 10), padx=5, pady=5, width=20)
            gem_label.grid(row=current_row, column=2)
            current_row += 1
            self.build_preview_labels.append(gem_label)

    def render_build_resistances(self):
        current_row = 8
        for res, value in self.build_resistances.items():
            res_label = Label(self.window, text=f"{res}:{value}")
            res_label.config(font=("Courier", 10), padx=5, pady=5, width=20)
            res_label.grid(row=current_row, column=3)
            current_row += 1
            self.build_preview_labels.append(res_label)

    def render_build_preview(self):
        for label in self.build_preview_labels:
            label.destroy()
        self.render_build_skills()
        self.render_build_gem_slots()
        self.render_build_resistances()

    def update_build_data(self, armor_parts_data):
        self.reset_build_data()
        gen = (data for data in armor_parts_data if data is not None)
        for data in gen:

            self.build_resistances["Defence"] += int(data.get("defence"))
            self.build_resistances["Fire Resistance"] += int(data.get("fire_resistance"))
            self.build_resistances["Water Resistance"] += int(data.get("water_resistance"))
            self.build_resistances["Thunder Resistance"] += int(data.get("thunder_resistance"))
            self.build_resistances["Ice Resistance"] += int(data.get("ice_resistance"))
            self.build_resistances["Dragon Resistance"] += int(data.get("dragon_resistance"))

            self.build_gem_slots["Level 1"] += data.get("slots").count("gem_level_1")
            self.build_gem_slots["Level 2"] += data.get("slots").count("gem_level_2")
            self.build_gem_slots["Level 3"] += data.get("slots").count("gem_level_3")

            for skill_dict in data.get("skills"):
                if skill_dict.get("name") in self.build_skills:
                    self.build_skills[skill_dict.get("name")] += int(skill_dict.get("value"))
                    if self.build_skills[skill_dict.get("name")] > int(skills_data.get(skill_dict.get("name")).get("max_level")):
                        self.build_skills[skill_dict.get("name")] = int(skills_data.get(skill_dict.get("name")).get("max_level"))
                else:
                    self.build_skills[skill_dict.get("name")] = int(skill_dict.get("value"))
        self.render_build_preview()

    def reset_build_data(self):
        self.build_skills = dict()
        self.build_gem_slots = {
            "Level 1": 0,
            "Level 2": 0,
            "Level 3": 0
        }
        self.build_resistances = {
            "Defence": 0,
            "Fire Resistance": 0,
            "Water Resistance": 0,
            "Thunder Resistance": 0,
            "Ice Resistance": 0,
            "Dragon Resistance": 0
        }


class SkillFilters:

    def __init__(self, window, armor_parts_option_menus):
        self.armor_parts_option_menus = armor_parts_option_menus
        self.window = window
        self.skill_to_filter_current_row = 2
        self.skills_to_filter = []
        self.latest_skill_to_filter = StringVar()
        self.latest_skill_to_filter.set(value="Skill Choice")
        self.latest_skill_to_filter.trace_add("write", self.render_skills_to_filter)
        self.skill_filter_option_menu = OptionMenu(self.window, self.latest_skill_to_filter,
                                                   *SKILL_OPTIONS)

        self.skill_filter_option_menu.config(font=("Courier", 10), padx=5, pady=5, width=25)
        self.skill_filter_option_menu.grid(row=1, column=2, sticky="W")
        self.skills_to_filter_labels = []
        reset_button = Button(window, text="Reset Skill Filters", command=self.reset_filters)
        reset_button.config(font=("Courier", 10), padx=10, pady=5, width=20)
        reset_button.grid(row=1, column=3, sticky="W")

    def render_skills_to_filter(self, *args):
        self.skills_to_filter.append(self.latest_skill_to_filter.get())
        skill_to_filter_label = Label(self.window, text=self.latest_skill_to_filter.get())
        skill_to_filter_label.config(font=("Courier", 10), padx=5, pady=5, width=15)
        skill_to_filter_label.grid(row=self.skill_to_filter_current_row, column=2, sticky="W")
        self.skills_to_filter_labels.append(skill_to_filter_label)
        self.skill_to_filter_current_row += 1
        self.skills_to_filter.append(self.latest_skill_to_filter.get())
        for armor_part_option_menu in self.armor_parts_option_menus:
            armor_part_option_menu.update_available_options_on_skills(self.skills_to_filter)

    def reset_filters(self):
        print("button was pressed")
        self.skills_to_filter.clear()
        for label in self.skills_to_filter_labels:
            label.destroy()
        self.skills_to_filter_labels.clear()
        self.skill_to_filter_current_row = 2

        skill_to_filter_label = Label(self.window, text="Empty")
        skill_to_filter_label.config(font=("Courier", 10), padx=5, pady=5, width=15)
        skill_to_filter_label.grid(row=self.skill_to_filter_current_row, column=2, sticky="W")

        for option_menu in self.armor_parts_option_menus:
            option_menu.update_available_options_on_skills(self.skills_to_filter)



class GemFilters:

    def __init__(self, window, armor_parts_option_menus):
        self.armor_parts_option_menus = armor_parts_option_menus
        self.window = window
        self.gem_level_1 = IntVar()
        self.gem_level_2 = IntVar()
        self.gem_level_3 = IntVar()

        self.gem_filter_dict = {
            "gem_level_1": self.gem_level_1,
            "gem_level_2": self.gem_level_2,
            "gem_level_3": self.gem_level_3
        }
        self.gem_checkboxes = []
        self.gem_checkboxes_vars = [self.gem_level_1, self.gem_level_2, self.gem_level_3]


        self.gem_level_1_option = Checkbutton(self.window, text="Gem Level 1", variable=self.gem_level_1, command=self.apply_gem_filters)
        self.gem_level_1_option.config(font=("Courier", 10), padx=5, pady=5, width=15)
        self.gem_level_1_option.grid(row=1, column=4)
        self.gem_checkboxes.append(self.gem_level_1_option)

        self.gem_level_2_option = Checkbutton(self.window, text="Gem Level 2", variable=self.gem_level_2, command=self.apply_gem_filters)
        self.gem_level_2_option.config(font=("Courier", 10), padx=5, pady=5, width=15)
        self.gem_level_2_option.grid(row=2, column=4)
        self.gem_checkboxes.append(self.gem_level_2_option)

        self.gem_level_3_option = Checkbutton(self.window, text="Gem Level 3", variable=self.gem_level_3, command=self.apply_gem_filters)
        self.gem_level_3_option.config(font=("Courier", 10), padx=5, pady=5, width=15)
        self.gem_level_3_option.grid(row=3, column=4)
        self.gem_checkboxes.append(self.gem_level_3_option)

    def apply_gem_filters(self):
        for armor_parts_option_menu in armor_parts_option_menus:
            armor_parts_option_menu.update_available_options_on_gems(self.gem_filter_dict)


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


def create_starting_page():

    clear_widgets()
    greeting_label = Label(window, text="Welcome to Monster Hunter Sets Builder!")
    greeting_label.config(font=("Courier", 30), pady=30)
    greeting_label.grid(row=0, column=0)

    skills_sets_builder_btn = Button(window, text="Skills Based Sets Builder", command=create_skill_based_builds_page)
    skills_sets_builder_btn.config(font=("Courier", 15), padx=5, pady=10, width=25)
    skills_sets_builder_btn.grid(row=1, column=0, sticky="W")

    manual_sets_builder_btn = Button(window, text="Manual Sets Builder", command=something_else)
    manual_sets_builder_btn.config(font=("Courier", 15), padx=5, pady=10, width=25)
    manual_sets_builder_btn.grid(row=2, column=0, sticky="W")


def something_else():
    first_col_row_pos = 0
    clear_widgets()
    armor_parts_label = Label(window, text="Armor Parts")
    armor_parts_label.config(font=("Courier", 12), pady=10, padx=5, width=15)
    armor_parts_label.grid(row=first_col_row_pos, column=0, columnspan=2)

    choice_options_label = Label(window, text="Skills Filters")
    choice_options_label.config(font=("Courier", 12), pady=5, padx=15, width=15)
    choice_options_label.grid(row=first_col_row_pos, column=2, columnspan=2)

    gem_options_label = Label(window, text="Gems Filters")
    gem_options_label.config(font=("Courier", 12), pady=5, padx=15, width=15)
    gem_options_label.grid(row=first_col_row_pos, column=4, columnspan=1)

    latest_item_preview_label = Label(window, text="Armor Part Preview")
    latest_item_preview_label.config(font=("Courier", 12), padx=5, pady=20, width=20)
    latest_item_preview_label.grid(row=6, column=0, sticky="W")

    build_preview_label = Label(window, text="Build Preview")
    build_preview_label.config(font=("Courier", 12), padx=5, pady=20, width=20)
    build_preview_label.grid(row=6, column=1, columnspan=3)

    build_total_skills_label = Label(window, text="Skills")
    build_total_skills_label.config(font=("Courier", 12), padx=10, pady=5, width=20)
    build_total_skills_label.grid(row=7, column=1)

    build_gem_slots_label = Label(window, text="Gem Slots")
    build_gem_slots_label.config(font=("Courier", 12), padx=10, pady=5, width=20)
    build_gem_slots_label.grid(row=7, column=2)

    build_res_label = Label(window, text="Resistances")
    build_res_label.config(font=("Courier", 12), padx=10, pady=5, width=20)
    build_res_label.grid(row=7, column=3)

    starting_page_btn = Button(window, text="Starting Page", command=create_starting_page)
    starting_page_btn.config(font=("Courier", 15), width=15, padx=10, pady=10)
    starting_page_btn.grid(row=30, column=0, sticky="W", pady=30)


    first_col_row_pos +=1
    build_preview = BuildPreview(window)
    #Print the armor parts positions=types
    for armor_pos in ARMOR_PART_POS:
        armor_position_label = Label(window, text=armor_pos + " : ")
        armor_position_label.config(font=("Courier", 10), pady=5, padx=5, width=10)
        armor_position_label.grid(row=first_col_row_pos, column=0, sticky="W")
        armor_parts_option_menus.append(ArmorPartOption(first_col_row_pos, 1, armor_pos, window, build_preview))
        first_col_row_pos += 1


    option_filters = SkillFilters(window, armor_parts_option_menus)
    gem_filters = GemFilters(window, armor_parts_option_menus)


def create_skill_based_builds_page():
    clear_widgets()

    option_menus = []
    talisman_skills = []
    talisman_gems = []
    weapon_gems = []
    gems = []

    skill_options_header = Label(window, text="Skill Choices")
    skill_options_header.config(font=("Courier", 20), width=30)
    skill_options_header.grid(row=0, column=0)

    skill_level_header = Label(window, text="Max Skill Level")
    skill_level_header.config(font=("Courier", 20), width=30)
    skill_level_header.grid(row=0, column=1)

    starting_page_btn = Button(window, text="Starting Page", command=create_starting_page)
    starting_page_btn.config(font=("Courier", 15), width=15, padx=10, pady=10)
    starting_page_btn.grid(row=30, column=0, sticky="W")

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


def create_armor_set_page(best_builds, btn_type="next", number_to_display=0):
    print(best_builds)
    clear_widgets()
    global build_number_to_display
    if btn_type == "next":
        build_number_to_display += 1
    else:
        build_number_to_display -= 1
    if build_number_to_display >= len(best_builds) or build_number_to_display < 0:
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

    starting_page_btn = Button(window, text="Starting Page", command=create_starting_page)
    starting_page_btn.config(font=("Courier", 15), width=15, padx=10, pady=10)
    starting_page_btn.grid(row=30, column=0, sticky="W", pady=30)

    next_build_btn = Button(window, text="Next Build", command= lambda: create_armor_set_page(best_builds, "next", build_number_to_display))
    next_build_btn.config(font=("Courier", 15), width=15, padx=20, pady=10)
    next_build_btn.grid(row=30, column=2)

    previous_build_btn = Button(window, text="Previous Build", command= lambda: create_armor_set_page(best_builds, "previous", build_number_to_display))
    previous_build_btn.config(font=("Courier", 15), width=15, padx=20, pady=10)
    if build_number_to_display > 0:
        previous_build_btn.grid(row=30, column=1)


create_starting_page()
window.mainloop()


