from orpheus.settings import SettingGroup, SettingItem, SettingsModal


def test_setting_item_change_value():
    item_toggle = SettingItem(
        key="matrix", label="Matrix Rain", kind="toggle", options=[True, False], value=True
    )
    item_toggle.cycle_next()
    assert item_toggle.value is False
    item_toggle.cycle_prev()
    assert item_toggle.value is True

    item_select = SettingItem(
        key="theme",
        label="Theme",
        kind="select",
        options=["cyberpunk", "matrix", "dracula"],
        value="cyberpunk",
    )
    item_select.cycle_next()
    assert item_select.value == "matrix"
    item_select.cycle_next()
    assert item_select.value == "dracula"
    item_select.cycle_next()
    assert item_select.value == "cyberpunk"


def test_settings_modal_navigation():
    g1 = SettingGroup(
        title="Visuals",
        items=[
            SettingItem(
                key="theme",
                label="Theme",
                kind="select",
                options=["cyberpunk", "matrix"],
                value="cyberpunk",
            ),
            SettingItem(
                key="anim",
                label="Animation",
                kind="select",
                options=["Pulse", "Wave", "None"],
                value="Pulse",
            ),
        ],
    )
    modal = SettingsModal(groups=[g1])
    assert modal.current_index == 0
    modal.action_next_item()
    assert modal.current_index == 1
    modal.action_prev_item()
    assert modal.current_index == 0
