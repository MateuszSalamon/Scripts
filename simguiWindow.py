import os, schedule, time
import pandas as pd
from typing import Dict, Any, Callable
from enum import Enum

try:
    import dearpygui.dearpygui as dpg
    DPG_AVAILABLE = True
except Exception:
    dpg = None
    DPG_AVAILABLE = False

VERSION = 'v1.0'

class MsgValid(Enum):
    VALID = 0,
    INVALID = 1

class DbConfigMan:
    """ Class for messages database management """
    __DB_FILE_PATH = r'candb\db.csv'
    __DB_H_NAME, __DB_H_ID, __DB_H_PAYLOAD, __DB_H_PERIOD_EN, __DB_H_PERIOD = \
        'name', 'id', 'payload', 'period_en', 'period'
    __DB_DF_HEADERS = [__DB_H_NAME, __DB_H_ID, __DB_H_PAYLOAD, __DB_H_PERIOD_EN, __DB_H_PERIOD]

    def __init__(self):
        self.__msg_config_df = None
        self.__create_db_config_file()
        self.__load_db_config_from_file()

    def __create_db_config_file(self) -> None:
        """ Create db file if does not exist """
        if not os.path.exists(self.__DB_FILE_PATH):
            self.__msg_config_df = pd.DataFrame(columns=self.__DB_DF_HEADERS)
            if not os.path.exists(os.path.dirname(self.__DB_FILE_PATH)):
                os.mkdir(os.path.dirname(self.__DB_FILE_PATH))
            self.__msg_config_df.to_csv(self.__DB_FILE_PATH, index=False)
            print('Created db file: {}'.format(self.__DB_FILE_PATH))
        else:
            """ Db config file already exists, do nothing """
            pass

    def __load_db_config_from_file(self) -> None:
        """ Load configuration from db file """
        self.__msg_config_df = pd.read_csv(self.__DB_FILE_PATH)
        print('Read db file:\n{}'.format(self.__msg_config_df))

    def __save_db_config_to_file(self) -> None:
        """ Save configuration to file """
        self.__msg_config_df.to_csv(self.__DB_FILE_PATH + '.temp', index=False)
        os.remove(self.__DB_FILE_PATH)
        os.rename(self.__DB_FILE_PATH + '.temp', self.__DB_FILE_PATH)

    def __update_db_config(self, new_config_db: pd.DataFrame) -> None:
        """ Update msg configuration """
        self.__msg_config_df = new_config_db
        self.__save_db_config_to_file()

    @staticmethod
    def __is_msg_valid(msg_id: str, payload: str) -> MsgValid:
        """ Check if message is valid """
        if msg_id.count('0x') == 1 and len(msg_id) > 2:
            """ Provided msg id contains hex symbol as expected """
            try:
                hex_val = int(msg_id, 16)
            except ValueError:
                """ Provided value contain invalid characters """
                print('MSG INVALID: Provided id contains invalid characters!')
            else:
                """ Provided id value is correct """
                pld_char_len = len(payload)
                expected_values_num = int((pld_char_len + 1) / 5)
                spaces_num, hex_num = payload.count(' '), payload.count('0x')
                if ((pld_char_len + 1) % 5 == 0 and spaces_num == expected_values_num - 1 and
                        hex_num == expected_values_num and expected_values_num <= 8):
                    try:
                        hex_vals = [int(val, 16) for val in payload.split(sep=' ')]
                    except ValueError:
                        """ Provided values contain invalid characters """
                        print('MSG INVALID: Provided payload contains invalid characters!')
                    else:
                        """ Provided payload values are correct """
                        return MsgValid.VALID
                else:
                    """ Provided payload is not as expected """
                    print('MSG INVALID: Provided payload is invalid!')
        else:
            """ Provided msg id not in hex """
            print('MSG INVALID: Provided msg id is not valid hex!')

        return MsgValid.INVALID

    """ ============================================= Class interface ============================================= """

    def add_msg(self, name: str, msg_id: str, payload: str) -> bool:
        """ Add new message to db file """
        if MsgValid.VALID == self.__is_msg_valid(msg_id=msg_id, payload=payload):
            """ Provided message is valid """
            new_msg_config_df = self.__msg_config_df.append(pd.DataFrame((
                [[name, msg_id, payload, False, str(100)]]), columns=self.__DB_DF_HEADERS), ignore_index=True)
            self.__update_db_config(new_config_db=new_msg_config_df)
            print('Added message to db file:\n{}'.format(new_msg_config_df.iloc[[-1]]))
            return True
        else:
            """ Provided message is invalid """
            return False

    def delete_msg(self, index: int) -> None:
        """ Remove message from db file """
        print('delete msg:', self.__msg_config_df.loc[index, 'id'])
        new_msg_config_df = self.__msg_config_df.drop(index=index)
        new_msg_config_df.reset_index(drop=True, inplace=True)
        self.__update_db_config(new_config_db=new_msg_config_df)

    def modify_msg(self, index: int, name: str, msg_id: str, payload: str, period_en: bool) -> bool:
        """ Modify already existing message in db filr """
        if MsgValid.VALID == self.__is_msg_valid(msg_id=msg_id, payload=payload):
            upd_msg_config_df = self.__msg_config_df
            upd_msg_config_df.at[index, self.__DB_H_NAME] = name
            upd_msg_config_df.at[index, self.__DB_H_ID] = msg_id
            upd_msg_config_df.at[index, self.__DB_H_PAYLOAD] = payload
            upd_msg_config_df.at[index, self.__DB_H_PERIOD_EN] = period_en
            self.__update_db_config(new_config_db=upd_msg_config_df)
            print('Modified message in db file:\n{}'.format(upd_msg_config_df.iloc[[index]]))
            return True
        else:
            """ Provided message is invalid """
            print('Message not updated!')
            return False

    def get_msg_config(self) -> pd.DataFrame:
        """ Provide messages configuration """
        return self.__msg_config_df

def on_exit(self):
    print("GUI closing")
    exit(0)

class SimGui:
    __TAB_H_NO, __TAB_H_NAME, __TAB_H_ID, __TAB_H_PAYLOAD, __TAB_H_MODIFY, __TAB_H_DEL, __TAB_H_EN, __TAB_H_SEND = \
        'no', 'name', 'id', 'payload', 'modify', 'delete', '100ms', 'send'
    __TAB_W_NO, __TAB_W_NAME, __TAB_W_ID, __TAB_W_PAYLOAD, __TAB_W_MODIFY, __TAB_W_DEL, __TAB_W_EN, __TAB_W_SEND = \
        50, 250, 100, 300, 50, 50, 50, 50
    __COLUMN_NAMES = [__TAB_H_NO, __TAB_H_NAME, __TAB_H_ID, __TAB_H_PAYLOAD, __TAB_H_MODIFY, __TAB_H_DEL, __TAB_H_EN,
                      __TAB_H_SEND]
    __COLUMN_WIDTHS = [__TAB_W_NO, __TAB_W_NAME, __TAB_W_ID, __TAB_W_PAYLOAD, __TAB_W_MODIFY, __TAB_W_DEL, __TAB_W_EN,
                       __TAB_W_SEND]

    def __init__(self, switch_sim_en_h: Callable, add_msg_h: Callable, delete_msg_h: Callable, modify_msg_h: Callable,
                 get_msg_config_h: Callable, send_msg_trig_h: Callable):
        """ Setup external handlers """
        self.__switch_sim_en_h = switch_sim_en_h
        self.__add_msg_h = add_msg_h
        self.__delete_msg_h = delete_msg_h
        self.__modify_msg_h = modify_msg_h
        self.__get_msg_config_h = get_msg_config_h
        self.__send_msg_trig_h = send_msg_trig_h

    def __display_table(self):
        """ Display messages configuration from db file """

        if not DPG_AVAILABLE:
            return

        # Retrieve message config DataFrame
        if callable(self.__get_msg_config_h):
            msg_config_df = self.__get_msg_config_h()
        else:
            msg_config_df = pd.DataFrame(columns=['name', 'id', 'payload', 'period_en', 'period'])

        # Remove existing table if present
        if dpg.does_item_exist('msg_table'):
            try:
                dpg.delete_item('msg_table')
            except Exception:
                pass

        with dpg.table(tag='msg_table', parent='PyCANSimMain', header_row=True):
            for col_name in self.__COLUMN_NAMES:
                dpg.add_table_column(label=col_name)

            # Add rows
            for index, (_, row) in enumerate(msg_config_df.iterrows()):
                with dpg.table_row():
                    dpg.add_text(str(index))
                    dpg.add_input_text(tag=f'it_name_{index}', width=self.__TAB_W_NAME - 10, default_value=str(row.get('name', '')), readonly=True)
                    dpg.add_input_text(tag=f'it_id_{index}', width=self.__TAB_W_ID - 10, default_value=str(row.get('id', '')), readonly=True)
                    dpg.add_input_text(tag=f'it_payload_{index}', width=self.__TAB_W_PAYLOAD - 10, default_value=str(row.get('payload', '')), readonly=True)
                    dpg.add_button(label=' ... ', tag=f'btn_modify_{index}', callback=self.__btn_modify_msg_clbk, user_data={'index': index, 'source_checkbox': False})
                    dpg.add_button(label='  x  ', tag=f'btn_del_{index}', callback=self.__btn_del_msg_clbk, user_data=index)
                    dpg.add_checkbox(tag=f'it_period_en_{index}', callback=self.__btn_modify_msg_clbk, user_data={'index': index, 'source_checkbox': True})
                    dpg.set_value(f'it_period_en_{index}', bool(row.get('period_en', False)))
                    dpg.add_button(label='  >  ', tag=f'btn_send_{index}', callback=self.__btn_send_clbk, user_data=index)

        dpg.add_separator(parent='PyCANSimMain')

        # Add new message modal window
        if not dpg.does_item_exist('Add Message'):
            with dpg.window(label='Add Message', modal=True, show=False, tag='Add Message'):
                dpg.add_text('Name:\t\t')
                dpg.add_input_text(tag='it_name_new', width=self.__TAB_W_PAYLOAD + 30, hint='e.g. NM3')
                dpg.add_text('Id:  \t\t')
                dpg.add_input_text(tag='it_id_new', width=self.__TAB_W_PAYLOAD + 30, hint='e.g. 0x510')
                dpg.add_text('Payload: \t')
                dpg.add_input_text(tag='it_payload_new', width=self.__TAB_W_PAYLOAD + 30, hint='e.g. 0x40 0x10 0x10 0x00 0x00 0x00 0x00 0x00')
                with dpg.group(horizontal=True):
                    dpg.add_button(tag='btn_add_msg_confirm', label='Add', width=75, height=25, callback=lambda s, a: self.__btn_add_msg_clbk(s, False))
                    dpg.add_button(tag='btn_add_msg_cancel', label='Cancel', width=75, height=25, callback=lambda s, a: self.__btn_add_msg_clbk(s, True))

    def __update_msg_table(self):
        """ Reload messages configuration table """
        if DPG_AVAILABLE and dpg.does_item_exist('msg_table'):
            try:
                dpg.delete_item('msg_table')
            except Exception:
                pass
        if DPG_AVAILABLE and dpg.does_item_exist('Add Message'):
            try:
                dpg.delete_item('Add Message')
            except Exception:
                pass
        self.__display_table()

    def __btn_switch_sim_en_clbk(self, sender: str, sim_en: bool) -> None:
        """ Callback for start/stop simmulation buttons """
        dpg.configure_item('btn_start_sim', enabled=not sim_en)
        dpg.configure_item('btn_stop_sim', enabled=sim_en)
        self.__switch_sim_en_h(sim_en=sim_en)

    def __btn_add_msg_clbk(self, sender: str, is_cancel=False) -> None:
        """ Callback for add message/cancel buttons """
        if not DPG_AVAILABLE:
            return
        if is_cancel:
            if dpg.does_item_exist('Add Message'):
                dpg.configure_item('Add Message', show=False)
        else:
            name = dpg.get_value('it_name_new') if dpg.does_item_exist('it_name_new') else ''
            msg_id = dpg.get_value('it_id_new') if dpg.does_item_exist('it_id_new') else ''
            payload = dpg.get_value('it_payload_new') if dpg.does_item_exist('it_payload_new') else ''
            if callable(self.__add_msg_h) and self.__add_msg_h(name=name, msg_id=msg_id, payload=payload):
                self.__update_msg_table()

    def __btn_del_msg_clbk(self, sender: str, app_data: Any, user_data: int) -> None:
        """ Callback for delete message buttons """
        self.__delete_msg_h(index=user_data)
        self.__update_msg_table()

    def __btn_modify_msg_clbk(self, sender: str, app_data: Any, user_data: Dict[str, Any]) -> None:
        """ Callback for modify message buttons """
        print(f"Modify callback: sender={sender}, user_data={user_data}")

        """ Check if this is first step for modification - clicked modify button """
        btn_tag = f'btn_modify_{user_data["index"]}'

        # Check configuration to determine state
        config = dpg.get_item_configuration(btn_tag)
        current_label = config.get('label', '')
        print(f"Button config label: '{current_label}'")

        # If label is ' ... ', we are in readonly mode. If ' /ok ', we are in edit mode.
        is_editing = (current_label == ' /ok ')
        print(f"Is editing: {is_editing}")

        if not is_editing and not user_data['source_checkbox']:
            print("Entering edit mode")
            """ Clicked modify button - enable editing"""
            dpg.configure_item(f'it_name_{user_data["index"]}', readonly=False)
            dpg.configure_item(f'it_id_{user_data["index"]}', readonly=False)
            dpg.configure_item(f'it_payload_{user_data["index"]}', readonly=False)
            dpg.configure_item(btn_tag, label=' /ok ')
        else:
            print("Saving changes")
            """ Save updated values """
            name = dpg.get_value(f'it_name_{user_data["index"]}') if dpg.does_item_exist(f'it_name_{user_data["index"]}') else ''
            msg_id = dpg.get_value(f'it_id_{user_data["index"]}') if dpg.does_item_exist(f'it_id_{user_data["index"]}') else ''
            payload = dpg.get_value(f'it_payload_{user_data["index"]}') if dpg.does_item_exist(f'it_payload_{user_data["index"]}') else ''
            period_en = dpg.get_value(f'it_period_en_{user_data["index"]}') if dpg.does_item_exist(f'it_period_en_{user_data["index"]}') else False

            print(f"Values to save: name='{name}', id='{msg_id}', payload='{payload}', period_en={period_en}")

            if callable(self.__modify_msg_h) and self.__modify_msg_h(index=user_data['index'], name=name, msg_id=msg_id, payload=payload, period_en=period_en):
                print("Update successful")
                self.__update_msg_table()
            else:
                print("Update failed")
                """ Provided message is invalid """
                pass
    def __btn_send_clbk(self, sender: str, app_data: Any, user_data: int):
        """ Callback for send message buttons """
        self.__send_msg_trig_h(index=user_data)

    def on_exit(self):
        print("GUI closing")
        os._exit(0)

    """ ============================================= Class interface ============================================= """

    def run_gui(self):
        """ Start application gui """
        if not DPG_AVAILABLE:
            print('DearPyGUI not available, GUI disabled.')
            return

        dpg.create_context()
        dpg.create_viewport(title='pyCanSim' + ' ' + VERSION, width=1000, height=600)

        with dpg.window(label='PyCANSimMain', tag='PyCANSimMain'):
            dpg.add_text('pyCanSim ' + VERSION)
            dpg.add_spacer(height=5)
            with dpg.group(horizontal=True):
                dpg.add_button(label='Start simulation', tag='btn_start_sim', callback=lambda s, a: self.__btn_switch_sim_en_clbk(s, True))
                dpg.add_button(label='Stop simulation', tag='btn_stop_sim', callback=lambda s, a: self.__btn_switch_sim_en_clbk(s, False))
            dpg.add_spacer(height=5)
            dpg.add_button(label='Add message', tag='btn_add_msg', callback=lambda s, a: dpg.configure_item('Add Message', show=True))

        dpg.setup_dearpygui()
        dpg.set_exit_callback(self.on_exit)
        dpg.show_viewport()
        dpg.set_primary_window('PyCANSimMain', True)
        self.__display_table()
        dpg.start_dearpygui()
        dpg.destroy_context()



if __name__ == '__main__':
    # Simple in-memory storage for testing
    mock_db = []

    def get_config():
        if not mock_db:
            return pd.DataFrame(columns=['name', 'id', 'payload', 'period_en', 'period'])
        return pd.DataFrame(mock_db)

    def add_msg(name, msg_id, payload):
        mock_db.append({'name': name, 'id': msg_id, 'payload': payload, 'period_en': False, 'period': 0})
        return True

    def delete_msg(index):
        if 0 <= index < len(mock_db):
            mock_db.pop(index)

    def modify_msg(index, name, msg_id, payload, period_en):
        if 0 <= index < len(mock_db):
            mock_db[index].update({'name': name, 'id': msg_id, 'payload': payload, 'period_en': period_en})
            return True
        return False

    sim = SimGui(switch_sim_en_h=lambda s: print(f"Sim enabled: {s}"),
                 add_msg_h=add_msg,
                 delete_msg_h=delete_msg,
                 modify_msg_h=modify_msg,
                 get_msg_config_h=get_config,
                 send_msg_trig_h=lambda idx: print(f"Sending msg {idx}"))
    sim.run_gui()
