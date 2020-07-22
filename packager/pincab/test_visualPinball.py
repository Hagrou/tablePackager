from unittest import TestCase
import tempfile

from packager.pincab.visualPinball import *


class TestVisualPinball(TestCase):

    @staticmethod
    def write_and_extract_rom(vpx_sample: str) -> list:
        test_file = tempfile.TemporaryFile('wb', delete=False)
        test_file.write(bytearray(vpx_sample))
        test_file.close()
        roms = VisualPinball(None, None).extract_rom_name(test_file.name)
        os.unlink(test_file.name)
        return roms

    def test_extract_rom_from_star_trek(self):
        vpx_str = b"""
    '********************
    'Standard definitions
    '********************
    
        Const cGameName = "st_161h" 'change the romname here
    
         Const UseSolenoids = 1
         Const UseLamps = 0
         Const UseSync = 1
         Const HandleMech = 0 
    """
        roms = TestVisualPinball.write_and_extract_rom(vpx_str)
        self.assertListEqual(roms, ['st_161h'])

    def test_extract_rom_from_star_wars_trilogy(self):
        vpx_str = b"""
    With Controller
        cGameName = "swtril43" ' Latest rom version
        .GameName = cGameName
        .SplashInfoLine = "Star Wars Trilogy - Sega 1997" & vbNewLine & "VP9 table by JPSalas / Convert by Hanibal"
        .Games(cGameName).Settings.Value("rol") = 0 'dmd rotated
        .HandleMechanics = 0
        .HandleKeyboard = 0
        .ShowDMDOnly = 1
        .ShowFrame = 0
        .ShowTitle = 0
    """
        roms = TestVisualPinball.write_and_extract_rom(vpx_str)
        self.assertListEqual(roms, ['swtril43'])

    def test_extract_rom_from_medieval_madness(self):
        vpx_str = b"""
                    LoadVPM "01560000", "WPC.VBS", 3.46

    '********************
    'Standard definitions
    '********************

    dim bsTrough, bsCat, bsMe, bsMo, bsDa, DaLock, x, bump1, bump2, bump3, plungerIM

    'Const cGameName = "mm_10" 'Williams official rom
    'Const cGameName = "mm_109" 'free play only
    'Const cGameName="mm_109b" 'unofficial
    Const cGameName="mm_109c" 'unofficial profanity rom

    'Const SlingShotFLashers = 1
                    """
        roms = TestVisualPinball.write_and_extract_rom(vpx_str)
        self.assertListEqual(roms, ['mm_109c', 'mm_10', 'mm_109', 'mm_109b'])

    def test_extract_rom_from_pirate_of_the_caribbean(self):
        vpx_str = b"""
                    Plunger1.PullBack
	Controller.GameName="potc_600as"
 	'Controller.Games("POTC_600AS").Settings.Value("dmd_pos_x")=980
 	'Controller.Games("POTC_600AS").Settings.Value("dmd_pos_y")=766
 	'Controller.Games("POTC_600AS").Settings.Value("dmd_width")=290
 	'Controller.Games("POTC_600AS").Settings.Value("dmd_height")=768
	Controller.SplashInfoLine="Pirates of the Caribbean"
	Controller.ShowTitle=0
                    """
        roms = TestVisualPinball.write_and_extract_rom(vpx_str)
        self.assertListEqual(roms, ['potc_600as'])
