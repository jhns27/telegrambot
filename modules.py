import netsnmp
import datetime
import ipaddress
import time
import re
import constant
import puresnmp
from puresnmp.x690.types import Integer, OctetString


# Определение иерархии хоста
def get_type(host, model):
    if ipaddress.IPv4Address(host) in ipaddress.IPv4Network(constant.MO_switchs):
        get_type = "switches"
        return get_type
    else:
        get_type = "other"
        return get_type

def load_users(fund):
	b = 0
	users = open(f'{constant.WORK_DIR}/users.txt')
	users = users.readlines()
	load_users = []
	for user in users:
		user = int((users[b].split('='))[1])
		load_users.insert(b, user)
		b = b + 1
	return load_users

def load_id_users(chat_id):
	b = 0
	users = open(f'{constant.WORK_DIR}/users.txt')
	users = users.readlines()
	for user in users:
		if chat_id == int((users[b].split('='))[1]):
			return b
		b = b + 1
	return load_users


def back_to_user_keyboard(func):
    if func == "menu":
        reply_keyboard = [
            [f"{constant.MAGIC} Проверить устройство"],
        ]
    elif func == 'get_type == "switches"':
        reply_keyboard = [
            ["Состояние портов", "Проверить длину кабеля"],
            ["Выйти"],
        ]
    return reply_keyboard

# Определение модели устройтсва
def get_model(host):
    try:
        if ipaddress.IPv4Address(host) in ipaddress.IPv4Network(
            constant.MO_switchs
        ):
            model = netsnmp.snmpget(
                constant.oid_model,
                DestHost=host,
                Version=2,
                Community=constant.ro_switchs,
            )[0].decode("utf-8")
            if "S2350" in model:
                model = "Huawei S2350-28TP-EI-AC"
            elif "S2320" in model:
                model = "Huawei S2320-28TP-EI-AC"
            elif "S5320-28TP-LI-AC" in model:
                model = "Huawei S5320-28TP-LI-AC"
            elif "S5320-28P-LI-AC" in model:
                model = "Huawei S5320-28P-LI-AC"
            elif "S6320-54C-EI-48S-AC" in model:
                model = "Huawei S6320-54C-EI-48S-AC"
            elif "DGS-3420-28SC" in model:
                model = "Dlink DGS-3420-28SC"
            elif "MES2324" in model:
                if "MES2324FB" in model:
                    model = "Eltex MES2324FB"
                elif "MES2324P" in model:
                    model = "Eltex MES2324P"
            elif "MES3324F" in model:
                model = "Eltex MES3324F"
            elif "MES2428" in model:
                model = "Eltex MES2428"
            elif "QTECH" == model:
                model = "Qtech QSW-2910-10T-POE"
            elif "QSW-2850-28T-AC" in model:
                model = "Qtech QSW-2850-28T-AC"
            elif "QSW-3470-10T-AC-POE" in model:
                model = "Qtech QSW-3470-10T-AC-POE"
            elif "QSW-3470-28T-AC-POE" in model:
                model = "Qtech QSW-3470-28T-AC-POE"
            elif "ZXR10 2928" in model:
                model = "ZTE 2928E"
            elif ("S3100-20TP" in model) | (model == "Switch"):
                model = "MAIPU 20TP"
            elif "S3100-9TP" in model:
                model = "MAIPU 9TP"
            elif "S3100-28TP" in model:
                model = "MAIPU 28TP"
            elif "DES-3200-10" in model:
                model = "D-Link DES-3200-10"
            elif "DES-3200-28" in model:
                model = "D-Link DES-3200-28"
            elif "DES-1228/ME" in model:
                model = "D-Link DES-1228/ME"
            elif "DES-1210-28/ME/B2" in model:
                model = "D-Link DES-1210-28/ME/B2"
            elif "DES-1210-28/ME/B3" in model:
                model = "D-Link DES-1210-28/ME/B3"
            elif "JetStream 24-Port Gigabit" in model:
                if "Stackable L2+ Managed Switch with 4 10G SFP+ Slots" in model:
                    model = "Tp-Link T2700G-28TQ"
                elif (
                    "L2 Managed Switch with 4 SFP Slots" in model
                    or "L2+ Managed Switch with 4 SFP Slots" in model
                ):
                    model = "Tp-Link T2600G-28TS"
            return model
    except AttributeError:
        model = "Ошибка"
        return model
    except ipaddress.AddressValueError:
        model = "Ошибка"
        return model

def basic_info(host, model):
    try:
        if ipaddress.IPv4Address(host) in ipaddress.IPv4Network(
            constant.MO_switchs
        ):
            try:
                sysname = (
                    netsnmp.snmpget(
                        constant.oid_sysname,
                        DestHost=host,
                        Version=2,
                        Community=constant.ro_switchs,
                    )
                )[0].decode("utf-8")
                uptime = (
                    netsnmp.snmpget(
                        constant.oid_uptime,
                        DestHost=host,
                        Version=2,
                        Community=constant.ro_switchs,
                    )
                )[0].decode("utf-8")
                uptime = int(uptime) / 100
                uptime = datetime.timedelta(seconds=uptime)
                result = f"{constant.UP} IP: {host}\nИмя устройства: {sysname}\nМодель устройства: {model}\nUptime: {uptime}"
                return result
            except:
                result = f"{constant.CRITICAL} Устройство не на связи"
                return result
    except ipaddress.AddressValueError:
        result = "Неверный IP"
        return result

def get_port_status(host, model):
    results = []
    result = ""
    if (
        (model == "Huawei S2350-28TP-EI-AC")
        | (model == "Huawei S2320-28TP-EI-AC")
        | (model == "Huawei S5320-28TP-LI-AC")
        | (model == "Huawei S5320-28P-LI-AC")
        | (model == "Tp-Link T2600G-28TS")
        | (model == "Tp-Link T2700G-28TQ")
    ):
        try:
            interface_range = calc_access_ports(host, model, "port status")
            result_inerrors = ""
            for interface, name_interface in zip(
                interface_range, constant.interface_list_28p
            ):
                get_descr_port = (
                    netsnmp.snmpget(
                        constant.oid_descr_ports + interface,
                        DestHost=host,
                        Version=2,
                        Community=constant.ro_switchs,
                    )
                )[0].decode("utf-8")
                get_oper_port = (
                    netsnmp.snmpget(
                        constant.oid_oper_ports + interface,
                        DestHost=host,
                        Version=2,
                        Community=constant.ro_switchs,
                    )
                )[0].decode("utf-8")
                get_inerrors = (
                    netsnmp.snmpget(
                        constant.oid_inerrors + interface,
                        DestHost=host,
                        Version=2,
                        Community=constant.ro_switchs,
                    )
                )[0].decode("utf-8")
                get_inerrors = int(get_inerrors)
                get_admin_port = (
                    netsnmp.snmpget(
                        constant.oid_admin_ports + interface,
                        DestHost=host,
                        Version=2,
                        Community=constant.ro_switchs,
                    )
                )[0].decode("utf-8")

                if get_oper_port == "1":
                    get_oper_port = constant.UP
                elif get_oper_port == "2":
                    get_oper_port = constant.DOWN
                else:
                    pass

                if get_admin_port == "2":
                    get_oper_port = f"{constant.WARNING} Выключен"

                if get_inerrors == 0:
                    results.append(
                        f"Порт {name_interface} {get_oper_port} | DESCR: {get_descr_port}"
                    )
                elif get_inerrors > 0:
                    result_inerrors = constant.DOWN
                    results.append(
                        f"Порт {name_interface} {get_oper_port} | DESCR: {get_descr_port} | Ошибки: {get_inerrors} {result_inerrors}"
                    )
            result = "\n".join(results)
            return result
        except:
            result = "Ошибка, попробуйте позднее"
            return result
    elif model == "Huawei S5320-36C-EI-28S-AC":
        try:
            interface_range = calc_access_ports(host, model, "port status")
            result_inerrors = ""
            for interface, name_interface in zip(
                interface_range, constant.interface_list_36p
            ):
                get_descr_port = (
                    netsnmp.snmpget(
                        constant.oid_descr_ports + interface,
                        DestHost=host,
                        Version=2,
                        Community=constant.ro_switchs,
                    )
                )[0].decode("utf-8")
                get_oper_port = (
                    netsnmp.snmpget(
                        constant.oid_oper_ports + interface,
                        DestHost=host,
                        Version=2,
                        Community=constant.ro_switchs,
                    )
                )[0].decode("utf-8")
                get_inerrors = (
                    netsnmp.snmpget(
                        constant.oid_inerrors + interface,
                        DestHost=host,
                        Version=2,
                        Community=constant.ro_switchs,
                    )
                )[0].decode("utf-8")
                get_inerrors = int(get_inerrors)
                get_admin_port = (
                    netsnmp.snmpget(
                        constant.oid_admin_ports + interface,
                        DestHost=host,
                        Version=2,
                        Community=constant.ro_switchs,
                    )
                )[0].decode("utf-8")

                if get_oper_port == "1":
                    get_oper_port = constant.UP
                elif get_oper_port == "2":
                    get_oper_port = constant.DOWN
                else:
                    pass

                if get_admin_port == "2":
                    get_oper_port = f"{constant.WARNING} Выключен"

                if get_inerrors == 0:
                    results.append(
                        f"Порт {name_interface} {get_oper_port} | DESCR: {get_descr_port}"
                    )
                elif get_inerrors > 0:
                    result_inerrors = constant.DOWN
                    results.append(
                        f"Порт {name_interface} {get_oper_port} | DESCR: {get_descr_port} | Ошибки: {get_inerrors} {result_inerrors}"
                    )
            result = "\n".join(results)
            return result
        except:
            result = "Ошибка, попробуйте позднее"
            return result
    elif model == "Huawei S6320-54C-EI-48S-AC":
        try:
            community = constant.ro_switchs
            interface_range = calc_access_ports(host, model, "port status")
            result_inerrors = ""
            for interface, name_interface in zip(
                interface_range, constant.interface_list_50p
            ):
                get_descr_port = (
                    netsnmp.snmpget(
                        constant.oid_descr_ports + interface,
                        DestHost=host,
                        Version=2,
                        Community=community,
                    )
                )[0].decode("utf-8")
                get_oper_port = (
                    netsnmp.snmpget(
                        constant.oid_oper_ports + interface,
                        DestHost=host,
                        Version=2,
                        Community=community,
                    )
                )[0].decode("utf-8")
                get_inerrors = (
                    netsnmp.snmpget(
                        constant.oid_inerrors + interface,
                        DestHost=host,
                        Version=2,
                        Community=community,
                    )
                )[0].decode("utf-8")
                get_inerrors = int(get_inerrors)
                get_admin_port = (
                    netsnmp.snmpget(
                        constant.oid_admin_ports + interface,
                        DestHost=host,
                        Version=2,
                        Community=community,
                    )
                )[0].decode("utf-8")

                if get_oper_port == "1":
                    get_oper_port = constant.UP
                elif get_oper_port == "2":
                    get_oper_port = constant.DOWN
                else:
                    pass

                if get_admin_port == "2":
                    get_oper_port = f"{constant.WARNING} Выключен"

                if get_inerrors == 0:
                    results.append(
                        f"Порт {name_interface} {get_oper_port} | DESCR: {get_descr_port}"
                    )
                elif get_inerrors > 0:
                    result_inerrors = constant.DOWN
                    results.append(
                        f"Порт {name_interface} {get_oper_port} | DESCR: {get_descr_port} | Ошибки: {get_inerrors} {result_inerrors}"
                    )
            result = "\n".join(results)
            return result
        except:
            result = "Ошибка, попробуйте позднее"
            return result
    elif (
        ("Eltex MES2324FB" == model)
        | ("Eltex MES2324P" == model)
        | ("Eltex MES3324F" == model)
        | ("Eltex MES2324" == model)
    ):
        try:
            interface_range = calc_access_ports(host, model, "port status")
            result_inerrors = ""
            for interface, name_interface in zip(
                interface_range, constant.interface_list_28p
            ):
                get_descr_port = (
                    netsnmp.snmpget(
                        constant.oid_descr_ports + interface,
                        DestHost=host,
                        Version=2,
                        Community=constant.ro_switchs,
                    )
                )[0].decode("utf-8")
                get_oper_port = (
                    netsnmp.snmpget(
                        constant.oid_oper_ports + interface,
                        DestHost=host,
                        Version=2,
                        Community=constant.ro_switchs,
                    )
                )[0].decode("utf-8")
                get_inerrors = (
                    netsnmp.snmpget(
                        constant.oid_inerrors + interface,
                        DestHost=host,
                        Version=2,
                        Community=constant.ro_switchs,
                    )
                )[0].decode("utf-8")
                get_inerrors = int(get_inerrors)
                get_admin_port = (
                    netsnmp.snmpget(
                        constant.oid_admin_ports + interface,
                        DestHost=host,
                        Version=2,
                        Community=constant.ro_switchs,
                    )
                )[0].decode("utf-8")

                if get_oper_port == "1":
                    get_oper_port = constant.UP
                elif get_oper_port == "2":
                    get_oper_port = constant.DOWN
                else:
                    pass

                if get_admin_port == "2":
                    get_oper_port = f"{constant.WARNING} Выключен"

                if get_inerrors == 0:
                    result_port = f"Порт {name_interface} {get_oper_port} | DESCR: {get_descr_port}"
                elif get_inerrors > 0:
                    result_inerrors = constant.DOWN
                    result_port = f"Порт {name_interface} {get_oper_port} | DESCR: {get_descr_port} | Ошибки: {get_inerrors} {result_inerrors}"

                
                results.append(f"{result_port}")
            result = "\n".join(results)
            return result
        except:
            result = "Ошибка, попробуйте позднее"
            return result
    elif (
        (model == "Qtech QSW-2910-10T-POE")
        | (model == "D-Link DES-3200-10")
        | (model == "Qtech QSW-3470-10T-AC-POE")
    ):
        try:
            result_inerrors = ""
            for interface in constant.interface_list_10p:
                get_descr_port = (
                    netsnmp.snmpget(
                        constant.oid_descr_ports + interface,
                        DestHost=host,
                        Version=2,
                        Community=constant.ro_switchs,
                    )
                )[0].decode("utf-8")
                get_oper_port = (
                    netsnmp.snmpget(
                        constant.oid_oper_ports + interface,
                        DestHost=host,
                        Version=2,
                        Community=constant.ro_switchs,
                    )
                )[0].decode("utf-8")
                get_inerrors = (
                    netsnmp.snmpget(
                        constant.oid_inerrors + interface,
                        DestHost=host,
                        Version=2,
                        Community=constant.ro_switchs,
                    )
                )[0].decode("utf-8")
                get_admin_port = (
                    netsnmp.snmpget(
                        constant.oid_admin_ports + interface,
                        DestHost=host,
                        Version=2,
                        Community=constant.ro_switchs,
                    )
                )[0].decode("utf-8")
                get_inerrors = int(get_inerrors)

                if get_oper_port == "1":
                    get_oper_port = constant.UP
                elif get_oper_port == "2":
                    get_oper_port = constant.DOWN
                else:
                    pass

                if get_admin_port == "2":
                    get_oper_port = f"{constant.WARNING} Выключен"

                if get_inerrors == 0:
                    results.append(
                        f"Порт {interface} {get_oper_port} | DESCR: {get_descr_port}"
                    )
                elif get_inerrors > 0:
                    result_inerrors = constant.DOWN
                    results.append(
                        f"Порт {interface} {get_oper_port} | DESCR: {get_descr_port} | Ошибки: {get_inerrors} {result_inerrors}"
                    )
            result = "\n".join(results)
            return result
        except:
            result = "Ошибка, попробуйте позднее"
            return result
    elif (
        (model == "Qtech QSW-2850-28T-AC")
        | (model == "D-Link DES-3200-28")
        | (model == "D-Link DES-1228/ME")
        | (model == "D-Link DES-1210-28/ME/B2")
        | (model == "D-Link DES-1210-28/ME/B3")
        | (model == "MAIPU 28TP")
        | (model == "ZTE 2928E")
        | (model == "Dlink DGS-3420-28SC")
        | (model == "Qtech QSW-3470-28T-AC-POE")
        | (model == "Eltex MES2428")
    ):
        try:
            result_inerrors = ""
            for interface in constant.interface_list_28p:
                get_descr_port = (
                    netsnmp.snmpget(
                        constant.oid_descr_ports + interface,
                        DestHost=host,
                        Version=2,
                        Community=constant.ro_switchs,
                    )
                )[0].decode("utf-8")
                get_oper_port = (
                    netsnmp.snmpget(
                        constant.oid_oper_ports + interface,
                        DestHost=host,
                        Version=2,
                        Community=constant.ro_switchs,
                    )
                )[0].decode("utf-8")
                get_inerrors = (
                    netsnmp.snmpget(
                        constant.oid_inerrors + interface,
                        DestHost=host,
                        Version=2,
                        Community=constant.ro_switchs,
                    )
                )[0].decode("utf-8")
                get_admin_port = (
                    netsnmp.snmpget(
                        constant.oid_admin_ports + interface,
                        DestHost=host,
                        Version=2,
                        Community=constant.ro_switchs,
                    )
                )[0].decode("utf-8")
                get_inerrors = int(get_inerrors)

                if get_oper_port == "1":
                    get_oper_port = constant.UP
                elif get_oper_port == "2":
                    get_oper_port = constant.DOWN
                else:
                    pass

                if get_admin_port == "2":
                    get_oper_port = f"{constant.WARNING} Выключен"


                if get_inerrors == 0:
                    results.append(
                        f"Порт {interface} {get_oper_port} | DESCR: {get_descr_port}"
                    )
                elif get_inerrors > 0:
                    result_inerrors = constant.DOWN
                    results.append(
                        f"Порт {interface} {get_oper_port} | DESCR: {get_descr_port} | Ошибки: {get_inerrors} {result_inerrors}"
                    )
            result = "\n".join(results)
            return result
        except:
            result = "Ошибка, попробуйте позднее"
            return result
    elif model == "MAIPU 9TP":
        try:
            result_inerrors = ""
            for interface in constant.interface_list_9p:
                get_descr_port = (
                    netsnmp.snmpget(
                        constant.oid_descr_ports + interface,
                        DestHost=host,
                        Version=2,
                        Community=constant.ro_switchs,
                    )
                )[0].decode("utf-8")
                get_oper_port = (
                    netsnmp.snmpget(
                        constant.oid_oper_ports + interface,
                        DestHost=host,
                        Version=2,
                        Community=constant.ro_switchs,
                    )
                )[0].decode("utf-8")
                get_inerrors = (
                    netsnmp.snmpget(
                        constant.oid_inerrors + interface,
                        DestHost=host,
                        Version=2,
                        Community=constant.ro_switchs,
                    )
                )[0].decode("utf-8")
                get_admin_port = (
                    netsnmp.snmpget(
                        constant.oid_admin_ports + interface,
                        DestHost=host,
                        Version=2,
                        Community=constant.ro_switchs,
                    )
                )[0].decode("utf-8")
                get_inerrors = int(get_inerrors)

                if get_oper_port == "1":
                    get_oper_port = constant.UP
                elif get_oper_port == "2":
                    get_oper_port = constant.DOWN
                else:
                    pass

                if get_admin_port == "2":
                    get_oper_port = f"{constant.WARNING} Выключен"

                if get_inerrors == 0:
                    results.append(
                        f"Порт {interface} {get_oper_port} | DESCR: {get_descr_port}"
                    )
                elif get_inerrors > 0:
                    result_inerrors = constant.DOWN
                    results.append(
                        f"Порт {interface} {get_oper_port} | DESCR: {get_descr_port} | Ошибки: {get_inerrors} {result_inerrors}"
                    )
            result = "\n".join(results)
            return result
        except:
            result = "Ошибка, попробуйте позднее"
            return result
    elif model == "MAIPU 20TP":
        try:
            result_inerrors = ""
            for interface in constant.interface_list_20p:
                get_descr_port = (
                    netsnmp.snmpget(
                        constant.oid_descr_ports + interface,
                        DestHost=host,
                        Version=2,
                        Community=constant.ro_switchs,
                    )
                )[0].decode("utf-8")
                get_oper_port = (
                    netsnmp.snmpget(
                        constant.oid_oper_ports + interface,
                        DestHost=host,
                        Version=2,
                        Community=constant.ro_switchs,
                    )
                )[0].decode("utf-8")
                get_inerrors = (
                    netsnmp.snmpget(
                        constant.oid_inerrors + interface,
                        DestHost=host,
                        Version=2,
                        Community=constant.ro_switchs,
                    )
                )[0].decode("utf-8")
                get_admin_port = (
                    netsnmp.snmpget(
                        constant.oid_admin_ports + interface,
                        DestHost=host,
                        Version=2,
                        Community=constant.ro_switchs,
                    )
                )[0].decode("utf-8")
                get_inerrors = int(get_inerrors)

                if get_oper_port == "1":
                    get_oper_port = constant.UP
                elif get_oper_port == "2":
                    get_oper_port = constant.DOWN
                else:
                    pass

                if get_admin_port == "2":
                    get_oper_port = f"{constant.WARNING} Выключен"

                if get_inerrors == 0:
                    results.append(
                        f"Порт {interface} {get_oper_port} | DESCR: {get_descr_port}"
                    )
                elif get_inerrors > 0:
                    result_inerrors = constant.DOWN
                    results.append(
                        f"Порт {interface} {get_oper_port} | DESCR: {get_descr_port} | Ошибки: {get_inerrors} {result_inerrors}"
                    )
            result = "\n".join(results)
            return result
        except:
            result = "Ошибка, попробуйте позднее"
            return result

def calc_access_ports(host, model, operation):
    results = []
    if operation == "port status":
        exe_community = constant.ro_switchs

        if model == "Huawei S2320-28TP-EI-AC":
            interfaces = constant.s2320_interfaces
        elif model == "Huawei S2350-28TP-EI-AC":
            interfaces = constant.s2350_interfaces
        elif (model == "Huawei S5320-28TP-LI-AC") | (model == "Huawei S5320-28P-LI-AC"):
            interfaces = constant.s5320_interfaces
        elif model == "Huawei S5320-36C-EI-28S-AC":
            interfaces = constant.s5320_36c_interfaces
        elif (
            (model == "Eltex MES2324FB")
            | (model == "Eltex MES2324P")
            | (model == "Eltex MES3324F")
            | (model == "Eltex MES2324")
        ):
            interfaces = constant.eltex_interfaces
        elif model == "Tp-Link T2600G-28TS":
            interfaces = constant.tplink_interfaces
        elif model == "Tp-Link T2700G-28TQ":
            interfaces = constant.tplink_interfaces2
        sess = netsnmp.Session(Version=2, DestHost=host, Community=exe_community)
        vars = netsnmp.VarList(netsnmp.Varbind(constant.oid_port_name))
        sess.walk(vars)
        for var in vars:
            newval = var.val
            newval = newval.decode("utf-8")
            if newval in interfaces:
                oid = var.tag
                oid = oid.split(".")
                results.append(oid[-1])
        return results
    elif operation == "cable diag":
        if model == "Huawei S2320-28TP-EI-AC":
            interfaces = constant.s2320_interfaces[0:24]
        elif model == "Huawei S2350-28TP-EI-AC":
            interfaces = constant.s2350_interfaces[0:24]
        elif (model == "Huawei S5320-28TP-LI-AC") | (model == "Huawei S5320-28P-LI-AC"):
            interfaces = constant.s5320_interfaces[0:24]
        elif model == "Tp-Link T2600G-28TS":
            interfaces = constant.tplink_interfaces[0:24]
        elif model == "Tp-Link T2700G-28TQ":
            interfaces = constant.tplink_interfaces2[0:24]
        sess = netsnmp.Session(
            Version=2, DestHost=host, Community=constant.ro_switchs
        )
        vars = netsnmp.VarList(netsnmp.Varbind(constant.oid_port_name))
        sess.walk(vars)
        for var in vars:
            newval = var.val
            newval = newval.decode("utf-8")
            if newval in interfaces:
                oid = var.tag
                oid = oid.split(".")
                results.append(oid[-1])
        return results

# Шоколад, функция проверки кабельной диагностики.
def get_cable_diag(host, model):
    OK_UP = "\U00002705 "
    OKEY = "\U00002611 "
    CROSSTALK = "\U000027B0 "
    SHORT = "\U0000274C "
    NOCABLE = "\U000026D4 "
    UNKNOWN = "\U0001F300 "
    results = []
    if "Huawei S5320" in model:
        huawei_range = calc_access_ports(host, model, "cable diag")
        for interface, name_interface in zip(
            huawei_range, constant.interface_list_24p
        ):
            get_oper_port = (
                netsnmp.snmpget(
                    constant.oid_oper_ports + interface,
                    DestHost=host,
                    Version=2,
                    Community=constant.ro_switchs,
                )
            )[0].decode("utf-8")
            get_admin_port = (
                netsnmp.snmpget(
                    constant.oid_admin_ports + interface,
                    DestHost=host,
                    Version=2,
                    Community=constant.ro_switchs,
                )
            )[0].decode("utf-8")
            if (get_oper_port == "2") & (get_admin_port == "1"):
                puresnmp.set(
                    host,
                    constant.rw_switchs,
                    f".1.3.6.1.4.1.2011.5.25.31.1.1.7.1.4.{interface}",
                    Integer(1),
                    timeout=10,
                )
                time.sleep(9)
                get_pair_a = netsnmp.snmpget(
                    constant.huawei_oid_pair_a + interface,
                    DestHost=host,
                    Version=2,
                    Community=constant.ro_switchs,
                )[0].decode("utf-8")
                status_pair_a = netsnmp.snmpget(
                    constant.huawei_oid_status_a + interface,
                    DestHost=host,
                    Version=2,
                    Community=constant.ro_switchs,
                )[0].decode("utf-8")
                get_pair_b = netsnmp.snmpget(
                    constant.huawei_oid_pair_b + interface,
                    DestHost=host,
                    Version=2,
                    Community=constant.ro_switchs,
                )[0].decode("utf-8")
                status_pair_b = netsnmp.snmpget(
                    constant.huawei_oid_status_b + interface,
                    DestHost=host,
                    Version=2,
                    Community=constant.ro_switchs,
                )[0].decode("utf-8")
                get_pair_c = netsnmp.snmpget(
                    constant.huawei_oid_pair_c + interface,
                    DestHost=host,
                    Version=2,
                    Community=constant.ro_switchs,
                )[0].decode("utf-8")
                status_pair_c = netsnmp.snmpget(
                    constant.huawei_oid_status_c + interface,
                    DestHost=host,
                    Version=2,
                    Community=constant.ro_switchs,
                )[0].decode("utf-8")
                get_pair_d = netsnmp.snmpget(
                    constant.huawei_oid_pair_d + interface,
                    DestHost=host,
                    Version=2,
                    Community=constant.ro_switchs,
                )[0].decode("utf-8")
                status_pair_d = netsnmp.snmpget(
                    constant.huawei_oid_status_d + interface,
                    DestHost=host,
                    Version=2,
                    Community=constant.ro_switchs,
                )[0].decode("utf-8")
                if (status_pair_a == "1") | (status_pair_a == "2"):
                    result_pair_a = OKEY
                elif (status_pair_a == "3") | (status_pair_a == "4"):
                    result_pair_a = SHORT
                elif status_pair_a == "5":
                    result_pair_a = CROSSTALK
                else:
                    result_pair_a = UNKNOWN

                if (status_pair_b == "1") | (status_pair_b == "2"):
                    result_pair_b = OKEY
                elif (status_pair_b == "3") | (status_pair_b == "4"):
                    result_pair_b = SHORT
                elif status_pair_b == "5":
                    result_pair_b = CROSSTALK
                else:
                    result_pair_b = UNKNOWN

                if (status_pair_c == "1") | (status_pair_c == "2"):
                    result_pair_c = OKEY
                elif (status_pair_c == "3") | (status_pair_c == "4"):
                    result_pair_c = SHORT
                elif status_pair_c == "5":
                    result_pair_c = CROSSTALK
                else:
                    result_pair_c = UNKNOWN

                if (status_pair_d == "1") | (status_pair_d == "2"):
                    result_pair_d = OKEY
                elif (status_pair_d == "3") | (status_pair_d == "4"):
                    result_pair_d = SHORT
                elif status_pair_d == "5":
                    result_pair_d = CROSSTALK
                else:
                    result_pair_d = UNKNOWN
                results.append(
                    f"Порт {name_interface} | А: {get_pair_a} м, STATE: {result_pair_a} | B: {get_pair_b} м, ST: {result_pair_b} | C: {get_pair_c} м, ST: {result_pair_c} | D: {get_pair_d} м, ST: {result_pair_d}"
                )
        result_cable_diag = "\n".join(results)
        result_cable_diag = f"{result_cable_diag}\nP.S. Состояния: {OKEY} - Всё хорошо, {CROSSTALK} - Пары перепутаны местами, {SHORT} - Короткое на паре, {NOCABLE} - Нет кабеля, {UNKNOWN} - Неизвестно "
        return result_cable_diag
    elif ("Huawei S2350" in model) | ("Huawei S2320" in model):
        huawei_range = calc_access_ports(host, model, "cable diag")
        for interface, name_interface in zip(
            huawei_range, constant.interface_list_24p
        ):
            get_oper_port = (
                netsnmp.snmpget(
                    constant.oid_oper_ports + interface,
                    DestHost=host,
                    Version=2,
                    Community=constant.ro_switchs,
                )
            )[0].decode("utf-8")
            get_admin_port = (
                netsnmp.snmpget(
                    constant.oid_admin_ports + interface,
                    DestHost=host,
                    Version=2,
                    Community=constant.ro_switchs,
                )
            )[0].decode("utf-8")
            if (get_oper_port == "2") & (get_admin_port == "1"):
                puresnmp.set(
                    host,
                    constant.rw_switchs,
                    f".1.3.6.1.4.1.2011.5.25.31.1.1.7.1.4.{interface}",
                    Integer(3),
                    timeout=6,
                )
                time.sleep(5)
                get_pair_a = netsnmp.snmpget(
                    constant.huawei_oid_pair_a + interface,
                    DestHost=host,
                    Version=2,
                    Community=constant.ro_switchs,
                )[0].decode("utf-8")
                status_pair_a = netsnmp.snmpget(
                    constant.huawei_oid_status_a + interface,
                    DestHost=host,
                    Version=2,
                    Community=constant.ro_switchs,
                )[0].decode("utf-8")
                get_pair_b = netsnmp.snmpget(
                    constant.huawei_oid_pair_b + interface,
                    DestHost=host,
                    Version=2,
                    Community=constant.ro_switchs,
                )[0].decode("utf-8")
                status_pair_b = netsnmp.snmpget(
                    constant.huawei_oid_status_b + interface,
                    DestHost=host,
                    Version=2,
                    Community=constant.ro_switchs,
                )[0].decode("utf-8")
                if (status_pair_a == "1") | (status_pair_a == "2"):
                    result_pair_a = OKEY
                elif (status_pair_a == "3") | (status_pair_a == "4"):
                    result_pair_a = SHORT
                elif status_pair_a == "5":
                    result_pair_a = CROSSTALK
                else:
                    result_pair_a = UNKNOWN

                if (status_pair_b == "1") | (status_pair_b == "2"):
                    result_pair_b = OKEY
                elif (status_pair_b == "3") | (status_pair_b == "4"):
                    result_pair_b = SHORT
                elif status_pair_b == "5":
                    result_pair_b = CROSSTALK
                else:
                    result_pair_b = UNKNOWN
                results.append(
                    f"Порт {name_interface} | А: {get_pair_a} м, STATE: {result_pair_a} | B: {get_pair_b} м, ST: {result_pair_b}"
                )
        result_cable_diag = "\n".join(results)
        result_cable_diag = f"{result_cable_diag}\nP.S. Состояния: {OKEY} - Всё хорошо, {CROSSTALK} - Пары перепутаны местами, {SHORT} - Короткое на паре, {NOCABLE} - Нет кабеля, {UNKNOWN} - Неизвестно "
        return result_cable_diag
    elif model == "Qtech QSW-2850-28T-AC":
        for interface in constant.interface_list_24p:
            get_oper_port = (
                netsnmp.snmpget(
                    constant.oid_oper_ports + interface,
                    DestHost=host,
                    Version=2,
                    Community=constant.ro_switchs,
                )
            )[0].decode("utf-8")
            get_admin_port = (
                netsnmp.snmpget(
                    constant.oid_admin_ports + interface,
                    DestHost=host,
                    Version=2,
                    Community=constant.ro_switchs,
                )
            )[0].decode("utf-8")
            if (get_oper_port == "2") & (get_admin_port == "1"):
                puresnmp.set(
                    host,
                    constant.rw_switchs,
                    f".1.3.6.1.4.1.27514.100.3.2.1.18.{interface}",
                    Integer(1),
                )
                time.sleep(2)
                get_status = (
                    netsnmp.snmpget(
                        constant.qtech_oid_result + interface,
                        DestHost=host,
                        Version=2,
                        Community=constant.ro_switchs,
                    )
                )[0].decode("utf-8")
                result_pair = get_status.split("\n")
                half_result_a = result_pair[-3]
                half_result_a = half_result_a.replace("(1, 2)", "")
                if (
                    ("open" in half_result_a)
                    | ("abnormal" in half_result_a)
                    | ("well" in half_result_a)
                ):
                    result_pair_a = OKEY
                elif "short" in half_result_a:
                    result_pair_a = SHORT
                else:
                    result_pair_a = UNKNOWN
                lengh_pair_a = re.findall(
                    "[0-9][0-9][0-9]|[0-9][0-9]|[0-9]", half_result_a
                )
                lengh_pair_a = lengh_pair_a[0]
                half_result_b = result_pair[-2]
                half_result_b = half_result_b.replace("(3, 6)", "")
                if (
                    ("open" in half_result_b)
                    | ("abnormal" in half_result_b)
                    | ("well" in half_result_b)
                ):
                    result_pair_b = OKEY
                elif "short" in half_result_b:
                    result_pair_b = SHORT
                else:
                    result_pair_b = UNKNOWN
                lengh_pair_b = re.findall(
                    "[0-9][0-9][0-9]|[0-9][0-9]|[0-9]", half_result_b
                )
                lengh_pair_b = lengh_pair_b[0]
                results.append(
                    f"Порт {interface} | Пара А: {lengh_pair_a} м, Статус: {result_pair_a} | Пара B: {lengh_pair_b} м, Cтатус: {result_pair_b}"
                )
        result_cable_diag = "\n".join(results)
        result_cable_diag = f"{result_cable_diag}\nP.S. Состояния: {OKEY} - Всё хорошо, {CROSSTALK} - Пары перепутаны местами, {SHORT} - Короткое на паре, {NOCABLE} - Нет кабеля"
        return result_cable_diag
    elif "Qtech QSW-3470" in model:
        interface_list = ""
        if model == "Qtech QSW-3470-10T-AC-POE":
            interface_list = constant.interface_list_8p
        elif model == "Qtech QSW-3470-28T-AC-POE":
            interface_list = constant.interface_list_24p
        for interface in interface_list:
            get_oper_port = (
                netsnmp.snmpget(
                    constant.oid_oper_ports + interface,
                    DestHost=host,
                    Version=2,
                    Community=constant.ro_switchs,
                )
            )[0].decode("utf-8")
            get_admin_port = (
                netsnmp.snmpget(
                    constant.oid_admin_ports + interface,
                    DestHost=host,
                    Version=2,
                    Community=constant.ro_switchs,
                )
            )[0].decode("utf-8")
            if (get_oper_port == "2") & (get_admin_port == "1"):
                puresnmp.set(
                    host,
                    constant.rw_switchs,
                    f".1.3.6.1.4.1.27514.100.3.2.1.18.{interface}",
                    Integer(1),
                )
                time.sleep(2)
                get_status = (
                    netsnmp.snmpget(
                        constant.qtech_oid_result + interface,
                        DestHost=host,
                        Version=2,
                        Community=constant.ro_switchs,
                    )
                )[0].decode("utf-8")
                result_pair = get_status.split("\n")
                half_result_a = result_pair[-5]
                half_result_a = half_result_a.replace("(1, 2)", "")
                if (
                    ("open" in half_result_a)
                    | ("abnormal" in half_result_a)
                    | ("well" in half_result_a)
                ):
                    result_pair_a = OKEY
                elif "short" in half_result_a:
                    result_pair_a = SHORT
                else:
                    result_pair_a = UNKNOWN
                lengh_pair_a = re.findall(
                    "[0-9][0-9][0-9]|[0-9][0-9]|[0-9]", half_result_a
                )
                lengh_pair_a = lengh_pair_a[0]
                half_result_b = result_pair[-4]
                half_result_b = half_result_b.replace("(3, 6)", "")
                if (
                    ("open" in half_result_b)
                    | ("abnormal" in half_result_b)
                    | ("well" in half_result_b)
                ):
                    result_pair_b = OKEY
                elif "short" in half_result_b:
                    result_pair_b = SHORT
                else:
                    result_pair_b = UNKNOWN
                lengh_pair_b = re.findall(
                    "[0-9][0-9][0-9]|[0-9][0-9]|[0-9]", half_result_b
                )
                lengh_pair_b = lengh_pair_b[0]
                half_result_c = result_pair[-3]
                half_result_c = half_result_c.replace("(4, 5)", "")
                if (
                    ("open" in half_result_c)
                    | ("abnormal" in half_result_c)
                    | ("well" in half_result_c)
                ):
                    result_pair_c = OKEY
                elif "short" in half_result_c:
                    result_pair_c = SHORT
                else:
                    result_pair_c = UNKNOWN
                lengh_pair_c = re.findall(
                    "[0-9][0-9][0-9]|[0-9][0-9]|[0-9]", half_result_c
                )
                lengh_pair_c = lengh_pair_c[0]
                half_result_d = result_pair[-2]
                half_result_d = half_result_d.replace("(7, 8)", "")
                if (
                    ("open" in half_result_d)
                    | ("abnormal" in half_result_d)
                    | ("well" in half_result_d)
                ):
                    result_pair_d = OKEY
                elif "short" in half_result_d:
                    result_pair_d = SHORT
                else:
                    result_pair_d = UNKNOWN
                lengh_pair_d = re.findall(
                    "[0-9][0-9][0-9]|[0-9][0-9]|[0-9]", half_result_d
                )
                lengh_pair_d = lengh_pair_d[0]
                results.append(
                    f"Порт {interface} | А: {lengh_pair_a} м, STATE: {result_pair_a} | B: {lengh_pair_b} м, ST: {result_pair_b} | C: {lengh_pair_c} м, ST: {result_pair_c} | D: {lengh_pair_d} м, ST: {result_pair_d}"
                )
        result_cable_diag = "\n".join(results)
        result_cable_diag = f"{result_cable_diag}\nP.S. Состояния: {OKEY} - Всё хорошо, {CROSSTALK} - Пары перепутаны местами, {SHORT} - Короткое на паре, {NOCABLE} - Нет кабеля"
        return result_cable_diag
    elif (
        (model == "D-Link DES-1228/ME")
        | (model == "D-Link DES-3200-28")
        | (model == "D-Link DES-3200-10")
    ):
        interface_list = ""
        if model == "D-Link DES-3200-10":
            interface_list = constant.interface_list_8p
        else:
            interface_list = constant.interface_list_24p
        for interface in interface_list:
            get_oper_port = (
                netsnmp.snmpget(
                    constant.old_dlink_oid_oper_ports + interface,
                    DestHost=host,
                    Version=2,
                    Community=constant.ro_switchs,
                )
            )[0].decode("utf-8")
            if get_oper_port == "0":
                get_oper_port = constant.DOWN
            elif get_oper_port == "1":
                get_oper_port = constant.UP
            elif get_oper_port == "2":
                get_oper_port = UNKNOWN
            puresnmp.set(
                host,
                constant.rw_switchs,
                f".1.3.6.1.4.1.171.12.58.1.1.1.12.{interface}",
                Integer(1),
            )
            time.sleep(1)
            get_result_cablediag = (
                netsnmp.snmpget(
                    constant.old_dlink_oid_status_cablediag + interface,
                    DestHost=host,
                    Version=2,
                    Community=constant.ro_switchs,
                )
            )[0].decode("utf-8")
            if get_result_cablediag != "2":
                get_pair_a = (
                    netsnmp.snmpget(
                        constant.old_dlink_oid_pair_a + interface,
                        DestHost=host,
                        Version=2,
                        Community=constant.ro_switchs,
                    )
                )[0].decode("utf-8")
                status_pair_a = (
                    netsnmp.snmpget(
                        constant.old_dlink_oid_status_a + interface,
                        DestHost=host,
                        Version=2,
                        Community=constant.ro_switchs,
                    )
                )[0].decode("utf-8")
                status_pair_a = str(status_pair_a)
                get_pair_b = (
                    netsnmp.snmpget(
                        constant.old_dlink_oid_pair_b + interface,
                        DestHost=host,
                        Version=2,
                        Community=constant.ro_switchs,
                    )
                )[0].decode("utf-8")
                status_pair_b = (
                    netsnmp.snmpget(
                        constant.old_dlink_oid_status_b + interface,
                        DestHost=host,
                        Version=2,
                        Community=constant.ro_switchs,
                    )
                )[0].decode("utf-8")
                status_pair_b = str(status_pair_b)
                if status_pair_a == "0":
                    result_pair_a = OK_UP
                elif status_pair_a == "1":
                    result_pair_a = OKEY
                elif (status_pair_a == "2") | (status_pair_a == "3"):
                    result_pair_a = SHORT
                elif status_pair_a == "4":
                    result_pair_a = CROSSTALK
                elif status_pair_a == "7":
                    result_pair_a = NOCABLE
                else:
                    result_pair_a = UNKNOWN

                if status_pair_b == "0":
                    result_pair_b = OK_UP
                elif status_pair_b == "1":
                    result_pair_b = OKEY
                elif (status_pair_b == "2") | (status_pair_b == "3"):
                    result_pair_b = SHORT
                elif status_pair_b == "4":
                    result_pair_b = CROSSTALK
                elif status_pair_b == "7":
                    result_pair_b = NOCABLE
                else:
                    result_pair_b = UNKNOWN
                results.append(
                    f"Порт {interface} {get_oper_port} | Пара А: {get_pair_a} м, STATE: {result_pair_a} | Пара B: {get_pair_b} м, STATE: {result_pair_b}"
                )
            else:
                get_result_cablediag = "Кабельная диагностика не смогла выполниться удачно, обратитесь к разработчику!"
                return get_result_cablediag
        result_cable_diag = "\n".join(results)
        result_cable_diag = f"{result_cable_diag}\nP.S. Состояния: {OK_UP} - Есть линк и всё хорошо, {OKEY} - Всё хорошо но линка нет, {CROSSTALK} - Пары перепутаны местами, {SHORT} - Короткое на паре, {NOCABLE} - Нет кабеля"
        return result_cable_diag
    elif (model == "D-Link DES-1210-28/ME/B2") | (model == "D-Link DES-1210-28/ME/B3"):
        if model == "D-Link DES-1210-28/ME/B2":
            oid_status_cablediag = constant.dlink_1210b2_oid_status_cablediag
            oid_pair_a = constant.dlink_1210b2_oid_pair_a
            oid_pair_b = constant.dlink_1210b2_oid_pair_b
            oid_status_a = constant.dlink_1210b2_oid_status_a
            oid_status_b = constant.dlink_1210b2_oid_status_b
        elif model == "D-Link DES-1210-28/ME/B3":
            oid_status_cablediag = constant.dlink_1210b3_oid_status_cablediag
            oid_pair_a = constant.dlink_1210b3_oid_pair_a
            oid_pair_b = constant.dlink_1210b3_oid_pair_b
            oid_status_a = constant.dlink_1210b3_oid_status_a
            oid_status_b = constant.dlink_1210b3_oid_status_b
        for interface in constant.interface_list_24p:
            get_oper_port = (
                netsnmp.snmpget(
                    constant.oid_oper_ports + interface,
                    DestHost=host,
                    Version=2,
                    Community=constant.ro_switchs,
                )
            )[0].decode("utf-8")
            if get_oper_port == "2":
                get_oper_port = constant.DOWN
            elif get_oper_port == "1":
                get_oper_port = constant.UP
            puresnmp.set(
                host,
                constant.rw_switchs,
                f"{oid_status_cablediag}{interface}",
                Integer(1),
            )
            time.sleep(1)
            get_result_cablediag = (
                netsnmp.snmpget(
                    oid_status_cablediag + interface,
                    DestHost=host,
                    Version=2,
                    Community=constant.ro_switchs,
                )
            )[0].decode("utf-8")
            if get_result_cablediag != "2":
                get_pair_a = (
                    netsnmp.snmpget(
                        oid_pair_a + interface,
                        DestHost=host,
                        Version=2,
                        Community=constant.ro_switchs,
                    )
                )[0].decode("utf-8")
                status_pair_a = (
                    netsnmp.snmpget(
                        oid_status_a + interface,
                        DestHost=host,
                        Version=2,
                        Community=constant.ro_switchs,
                    )
                )[0].decode("utf-8")
                status_pair_a = str(status_pair_a)
                get_pair_b = (
                    netsnmp.snmpget(
                        oid_pair_b + interface,
                        DestHost=host,
                        Version=2,
                        Community=constant.ro_switchs,
                    )
                )[0].decode("utf-8")
                status_pair_b = (
                    netsnmp.snmpget(
                        oid_status_b + interface,
                        DestHost=host,
                        Version=2,
                        Community=constant.ro_switchs,
                    )
                )[0].decode("utf-8")
                status_pair_b = str(status_pair_b)
                if (status_pair_a == "0") | (status_pair_a == "1"):
                    result_pair_a = OK_UP
                elif (status_pair_a == "2") | (status_pair_a == "3"):
                    result_pair_a = SHORT
                elif status_pair_a == "4":
                    result_pair_a = CROSSTALK
                elif status_pair_a == "7":
                    result_pair_a = NOCABLE
                else:
                    result_pair_a = UNKNOWN

                if (status_pair_b == "0") | (status_pair_b == "1"):
                    result_pair_b = OK_UP
                elif (status_pair_b == "2") | (status_pair_b == "3"):
                    result_pair_b = SHORT
                elif status_pair_b == "4":
                    result_pair_b = CROSSTALK
                elif status_pair_b == "7":
                    result_pair_b = NOCABLE
                else:
                    result_pair_b = UNKNOWN
                results.append(
                    f"Порт {interface} {get_oper_port} | Пара А: {get_pair_a} м, STATE: {result_pair_a} | Пара B: {get_pair_b} м, STATE: {result_pair_b}"
                )
            else:
                get_result_cablediag = "Кабельная диагностика не смогла выполниться удачно, обратитесь к разработчику!"
                return get_result_cablediag
        result_cable_diag = "\n".join(results)
        result_cable_diag = f"{result_cable_diag}\nP.S. Состояния: {OK_UP} - C парами всё хорошо, {CROSSTALK} - Пары перепутаны местами, {SHORT} - Короткое на паре, {NOCABLE} - Нет кабеля"
        return result_cable_diag
    elif model == "ZTE 2928E":
        firmware = (
            netsnmp.snmpget(
                constant.zte_oid_firmware,
                DestHost=host,
                Version=2,
                Community=constant.ro_switchs,
            )
        )[0].decode("utf-8")
        if firmware == "V2.05.12B36":
            for interface in constant.interface_list_24p:
                get_oper_port = int(
                    (
                        netsnmp.snmpget(
                            constant.oid_oper_ports + interface,
                            DestHost=host,
                            Version=2,
                            Community=constant.ro_switchs,
                        )
                    )[0].decode("utf-8")
                )
                get_admin_port = int(
                    (
                        netsnmp.snmpget(
                            constant.oid_admin_ports + interface,
                            DestHost=host,
                            Version=2,
                            Community=constant.ro_switchs,
                        )
                    )[0].decode("utf-8")
                )
                if (get_oper_port == 2) & (get_admin_port == 1):
                    puresnmp.set(
                        host,
                        constant.rw_switchs,
                        f".1.3.6.1.4.1.3902.15.2.30.11.1.1.2.{interface}",
                        Integer(1),
                    )
                    time.sleep(20)
                    try:
                        get_pair_a = (
                            netsnmp.snmpget(
                                constant.zte_oid_pair_a + interface,
                                DestHost=host,
                                Version=2,
                                Community=constant.ro_switchs,
                            )
                        )[0].decode("utf-8")
                        status_pair_a = (
                            netsnmp.snmpget(
                                constant.zte_oid_status_a + interface,
                                DestHost=host,
                                Version=2,
                                Community=constant.ro_switchs,
                            )
                        )[0].decode("utf-8")
                        status_pair_a = int(status_pair_a)
                        get_pair_b = (
                            netsnmp.snmpget(
                                constant.zte_oid_pair_b + interface,
                                DestHost=host,
                                Version=2,
                                Community=constant.ro_switchs,
                            )
                        )[0].decode("utf-8")
                        status_pair_b = (
                            netsnmp.snmpget(
                                constant.zte_oid_status_b + interface,
                                DestHost=host,
                                Version=2,
                                Community=constant.ro_switchs,
                            )
                        )[0].decode("utf-8")
                        status_pair_b = int(status_pair_b)
                    except:
                        get_pair_a = UNKNOWN
                        status_pair_a = UNKNOWN
                        get_pair_b = UNKNOWN
                        status_pair_b = UNKNOWN

                    if (status_pair_a == 1) | (status_pair_a == 2):
                        result_pair_a = OK_UP
                    elif status_pair_a == 5:
                        result_pair_a = UNKNOWN
                    else:
                        result_pair_a = SHORT

                    if (status_pair_b == 1) | (status_pair_b == 2):
                        result_pair_b = OK_UP
                    elif status_pair_b == 5:
                        result_pair_b = UNKNOWN
                    else:
                        result_pair_b = SHORT
                    results.append(
                        f"Порт {interface} | Пара А: {get_pair_a} м, STATE: {result_pair_a} | Пара B: {get_pair_b} м, STATE: {result_pair_b}"
                    )
            result_cable_diag = "\n".join(results)
            result_cable_diag = f"{result_cable_diag}\nP.S. Состояния: {OK_UP} - C парами всё хорошо, {CROSSTALK} - Пары перепутаны местами, {SHORT} - Короткое на паре, {NOCABLE} - Нет кабеля"
            return result_cable_diag
        else:
            result_cable_diag = "\nКоммутатор не поддерживает кабельную диагностику"
            return result_cable_diag
    elif (model == "Tp-Link T2600G-28TS") | (model == "Tp-Link T2700G-28TQ"):
        interface_range = calc_access_ports(host, model, "cable diag")
        for interface, name_interface in zip(
            interface_range, constant.interface_list_24p
        ):
            get_oper_port = (
                netsnmp.snmpget(
                    constant.oid_oper_ports + interface,
                    DestHost=host,
                    Version=2,
                    Community=constant.ro_switchs,
                )
            )[0].decode("utf-8")
            get_admin_port = (
                netsnmp.snmpget(
                    constant.oid_admin_ports + interface,
                    DestHost=host,
                    Version=2,
                    Community=constant.ro_switchs,
                )
            )[0].decode("utf-8")
            if (get_oper_port == "2") & (get_admin_port == "1"):
                puresnmp.set(
                    host,
                    constant.rw_switchs,
                    f".1.3.6.1.4.1.11863.6.8.1.3.1.0",
                    OctetString(f"1/0/{name_interface}".encode()),
                )
                time.sleep(3)
                get_pair_a = netsnmp.snmpget(
                    constant.tplink_oid_pair_a + interface,
                    DestHost=host,
                    Version=2,
                    Community=constant.ro_switchs,
                )[0].decode("utf-8")
                status_pair_a = netsnmp.snmpget(
                    constant.tplink_oid_status_a + interface,
                    DestHost=host,
                    Version=2,
                    Community=constant.ro_switchs,
                )[0].decode("utf-8")
                get_pair_b = netsnmp.snmpget(
                    constant.tplink_oid_pair_b + interface,
                    DestHost=host,
                    Version=2,
                    Community=constant.ro_switchs,
                )[0].decode("utf-8")
                status_pair_b = netsnmp.snmpget(
                    constant.tplink_oid_status_b + interface,
                    DestHost=host,
                    Version=2,
                    Community=constant.ro_switchs,
                )[0].decode("utf-8")
                get_pair_c = netsnmp.snmpget(
                    constant.tplink_oid_pair_c + interface,
                    DestHost=host,
                    Version=2,
                    Community=constant.ro_switchs,
                )[0].decode("utf-8")
                status_pair_c = netsnmp.snmpget(
                    constant.tplink_oid_status_c + interface,
                    DestHost=host,
                    Version=2,
                    Community=constant.ro_switchs,
                )[0].decode("utf-8")
                get_pair_d = netsnmp.snmpget(
                    constant.tplink_oid_pair_d + interface,
                    DestHost=host,
                    Version=2,
                    Community=constant.ro_switchs,
                )[0].decode("utf-8")
                status_pair_d = netsnmp.snmpget(
                    constant.tplink_oid_status_d + interface,
                    DestHost=host,
                    Version=2,
                    Community=constant.ro_switchs,
                )[0].decode("utf-8")
                if ("Open" in status_pair_a) | ("Normal" in status_pair_a):
                    result_pair_a = OKEY
                elif "Short" in status_pair_a:
                    result_pair_a = SHORT
                elif "Crosstalk" in status_pair_a:
                    result_pair_a = CROSSTALK
                else:
                    result_pair_a = UNKNOWN
                get_pair_a = re.findall("[0-9][0-9][0-9]|[0-9][0-9]|[0-9]", get_pair_a)
                get_pair_a = get_pair_a[0]
                if ("Open" in status_pair_b) | ("Normal" in status_pair_b):
                    result_pair_b = OKEY
                elif "Short" in status_pair_b:
                    result_pair_b = SHORT
                elif "Crosstalk" in status_pair_b:
                    result_pair_b = CROSSTALK
                else:
                    result_pair_b = UNKNOWN
                get_pair_b = re.findall("[0-9][0-9][0-9]|[0-9][0-9]|[0-9]", get_pair_b)
                get_pair_b = get_pair_b[0]
                if ("Open" in status_pair_c) | ("Normal" in status_pair_c):
                    result_pair_c = OKEY
                elif "Short" in status_pair_c:
                    result_pair_c = SHORT
                elif "Crosstalk" in status_pair_c:
                    result_pair_c = CROSSTALK
                else:
                    result_pair_c = UNKNOWN
                get_pair_c = re.findall("[0-9][0-9][0-9]|[0-9][0-9]|[0-9]", get_pair_c)
                get_pair_c = get_pair_c[0]
                if ("Open" in status_pair_d) | ("Normal" in status_pair_d):
                    result_pair_d = OKEY
                elif "Short" in status_pair_d:
                    result_pair_d = SHORT
                elif "Crosstalk" in status_pair_d:
                    result_pair_d = CROSSTALK
                else:
                    result_pair_d = UNKNOWN
                get_pair_d = re.findall("[0-9][0-9][0-9]|[0-9][0-9]|[0-9]", get_pair_d)
                get_pair_d = get_pair_d[0]
                results.append(
                    f"Порт {name_interface} | А: {get_pair_a} м, STATE: {result_pair_a} | B: {get_pair_b} м, ST: {result_pair_b} | C: {get_pair_c} м, ST: {result_pair_c} | D: {get_pair_d} м, ST: {result_pair_d}"
                )
        result_cable_diag = "\n".join(results)
        result_cable_diag = f"{result_cable_diag}\nP.S. Состояния: {OKEY} - Всё хорошо, {CROSSTALK} - Пары перепутаны местами, {SHORT} - Короткое на паре, {NOCABLE} - Нет кабеля, {UNKNOWN} - Неизвестно "
        return result_cable_diag
    else:
        result_cable_diag = "\nКоммутатор не поддерживает кабельную диагностику"
        return result_cable_diag