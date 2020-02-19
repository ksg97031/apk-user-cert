import os
import sys
import re
import click
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path
from subprocess import check_output

import shutil
from pathlib import Path
p = Path(__file__)
ROOT_DIR = p.parent.resolve()
TEMP_DIR = ROOT_DIR.joinpath('temp')
FILE_DIR = ROOT_DIR.joinpath('files')

binaries = ['apktool']
for binary in binaries:
    path = shutil.which(binary)
    if not path:
        raise Exception("Please download and set to your environment this file: " + binary)

    locals()[binary] = path

def run_apktool(option, apk_path: str):
    if isinstance(option, list):
        cmd = [apktool] + option + [apk_path]
    else:
        cmd = [apktool, option, apk_path]
    try:
        output = check_output(cmd)
    except:
        raise Exception("Error", " ".join(cmd))

    return True


@click.command()
@click.argument('apk_path')
def run(apk_path: str):
    apk_path = Path(apk_path)

    # APK decompile with apktool
    decompiled_path = TEMP_DIR.joinpath(str(apk_path.resolve())[:-4])
    if decompiled_path.exists():
        shutil.rmtree(decompiled_path)

    decompiled_path.mkdir()
    print("Decompiling ...")
    result = run_apktool(
        ['d', '-o', str(decompiled_path.resolve()), '-f'], str(apk_path.resolve()))

    if result:
        # android:networkSecurityConfig='@xml/network_security_config'
        android_manifest = decompiled_path.joinpath("AndroidManifest.xml")
        tree = ET.parse(str(android_manifest))
        root = tree.getroot()
        application = root.find('.//application')
        if '{http://schemas.android.com/apk/res/android}networkSecurityConfig' not in application.attrib:
            print("networkSecurityConfig attrib not founded")
            application.set('ns0:networkSecurityConfig', '@xml/network_security_config')
            tree.write(str(android_manifest))
            xml_path = decompiled_path.joinpath('res', 'xml', 'network_security_config.xml')
        else:
            print("networkSecurityConfig attrib founded", application.attrib['{http://schemas.android.com/apk/res/android}networkSecurityConfig'])
            config = application.attrib['{http://schemas.android.com/apk/res/android}networkSecurityConfig']
            xml_path = decompiled_path.joinpath(*(config.replace("@xml", "res/xml") + ".xml").split("/"))

        network_security_config = FILE_DIR.joinpath('network_security_config.xml')
        if not xml_path.exists():
            print("network_security_config.xml not founded")
            if not xml_path.parent.exists():
                xml_path.parent.mkdir(parents=True)
            shutil.copy(str(network_security_config), str(xml_path))
        else:
            # patch exist file
            print("network_security_config.xml founded")
            tree = ET.parse(str(xml_path))
            root = tree.getroot()

            bc_list = root.findall('base-config')
            if not bc_list:
                bc = ET.Element('base-config')
                ta = ET.Element('trust-anchors')
                bc.append(ta)
                root.append(bc)
            else:
                for bc in bc_list:
                    if not bc.find('trust-anchors'):
                        ta = ET.Element('trust-anchors')
                        bc.append(ta)

                tas_list = root.findall('.//trust-anchors')
                for tas in tas_list:
                    user_flag = False

                    certificates_list = tas.findall('certificates')
                    for certificates in certificates_list:
                        if certificates.attrib['src'] == 'user':
                            user_flag = True

                    if not user_flag:
                        e = ET.Element('certificates', attrib={'src':'user'})
                        tas.append(e)

            tree.write(str(xml_path))

        print("Rebuilding ...")
        result = run_apktool('b', str(decompiled_path.resolve()))
        apk_path = decompiled_path.joinpath('dist', apk_path.name)
        print(str(apk_path.resolve()))
        #shutil.rmtree(decompiled_path)


if __name__ == '__main__':
    run()

