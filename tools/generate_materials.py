#!/usr/bin/env python3
"""Generate constant per-texture MERS overrides for vanilla textures.
No Mojang albedo images are copied; only PBR response metadata is authored.
"""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'textures'/'blocks'
OUT.mkdir(parents=True,exist_ok=True)

def write(names, mers):
    for name in names:
        p=OUT/f'{name}.texture_set.json'
        obj={"format_version":"1.21.30","minecraft:texture_set":{"metalness_emissive_roughness_subsurface":mers}}
        p.write_text(json.dumps(obj,separators=(',',':'))+'\n',encoding='utf-8')

# Rough natural materials: distinct PBR response without replacing vanilla albedo.
STONE='''stone stone_granite stone_diorite stone_andesite cobblestone cobblestone_mossy stonebrick stonebrick_mossy stonebrick_cracked stonebrick_carved bedrock gravel tuff calcite dripstone_block deepslate deepslate_top cobbled_deepslate polished_deepslate deepslate_bricks deepslate_tiles blackstone blackstone_top blackstone_polished polished_blackstone_bricks end_stone end_bricks nether_brick red_nether_brick basalt_side basalt_top smooth_basalt'''.split()
POLISHED='''stone_granite_smooth stone_diorite_smooth stone_andesite_smooth stone_slab_top stone_slab_side polished_tuff polished_blackstone quartz_block_side quartz_block_top quartz_block_bottom quartz_block_lines quartz_block_lines_top purpur_block purpur_pillar purpur_pillar_top prismarine_bricks prismarine_dark'''.split()
EARTH='''dirt coarse_dirt dirt_podzol_top dirt_podzol_side rooted_dirt mud packed_mud mud_bricks clay grass_side_snowed mycelium_side mycelium_top farmland_dry farmland_wet'''.split()
SAND='''sand red_sand sandstone_normal sandstone_top sandstone_bottom sandstone_carved sandstone_smooth red_sandstone_normal red_sandstone_top red_sandstone_bottom red_sandstone_carved red_sandstone_smooth concrete_powder_white concrete_powder_orange concrete_powder_magenta concrete_powder_light_blue concrete_powder_yellow concrete_powder_lime concrete_powder_pink concrete_powder_gray concrete_powder_silver concrete_powder_cyan concrete_powder_purple concrete_powder_blue concrete_powder_brown concrete_powder_green concrete_powder_red concrete_powder_black'''.split()
WOOD='''planks_oak planks_spruce planks_birch planks_jungle planks_acacia planks_big_oak planks_mangrove planks_cherry planks_bamboo bamboo_planks crimson_planks warped_planks log_oak log_oak_top log_spruce log_spruce_top log_birch log_birch_top log_jungle log_jungle_top log_acacia log_acacia_top log_big_oak log_big_oak_top mangrove_log_side mangrove_log_top cherry_log_side cherry_log_top bamboo_block_side bamboo_block_top stripped_bamboo_block_side stripped_bamboo_block_top stripped_oak_log stripped_oak_log_top stripped_spruce_log stripped_spruce_log_top stripped_birch_log stripped_birch_log_top stripped_jungle_log stripped_jungle_log_top stripped_acacia_log stripped_acacia_log_top stripped_dark_oak_log stripped_dark_oak_log_top'''.split()
FOLIAGE='''grass_top grass_side grass_carried leaves_oak leaves_spruce leaves_birch leaves_jungle leaves_acacia leaves_big_oak leaves_mangrove leaves_cherry azalea_leaves azalea_leaves_flowered vine kelp_a kelp_b seagrass double_plant_grass_top double_plant_grass_bottom tallgrass fern large_fern_top large_fern_bottom bamboo_leaf bamboo_small_leaf mangrove_roots hanging_roots moss_block moss_carpet'''.split()
FLOWERS='''flower_dandelion flower_rose_blue orchid allium houstonia tulip_red tulip_orange tulip_white tulip_pink oxeye_daisy cornflower lily_of_the_valley sunflower_top sunflower_bottom peony_top peony_bottom rose_bush_top rose_bush_bottom lilac_top lilac_bottom pink_petals'''.split()
SNOW='''snow snow_block powder_snow'''.split()
GLASS='''glass glass_white glass_orange glass_magenta glass_light_blue glass_yellow glass_lime glass_pink glass_gray glass_silver glass_cyan glass_purple glass_blue glass_brown glass_green glass_red glass_black tinted_glass'''.split()
ICE='''ice packed_ice blue_ice frosted_ice_0 frosted_ice_1 frosted_ice_2 frosted_ice_3'''.split()
CERAMIC='''brick glazed_terracotta_white glazed_terracotta_orange glazed_terracotta_magenta glazed_terracotta_light_blue glazed_terracotta_yellow glazed_terracotta_lime glazed_terracotta_pink glazed_terracotta_gray glazed_terracotta_silver glazed_terracotta_cyan glazed_terracotta_purple glazed_terracotta_blue glazed_terracotta_brown glazed_terracotta_green glazed_terracotta_red glazed_terracotta_black concrete_white concrete_orange concrete_magenta concrete_light_blue concrete_yellow concrete_lime concrete_pink concrete_gray concrete_silver concrete_cyan concrete_purple concrete_blue concrete_brown concrete_green concrete_red concrete_black'''.split()
METAL_IRON='''iron_block iron_bars iron_trapdoor anvil_top_damaged_0 anvil_top_damaged_1 anvil_top_damaged_2 cauldron_side cauldron_bottom hopper_inside hopper_outside chain'''.split()
METAL_GOLD='''gold_block raw_gold_block'''.split()
METAL_COPPER='''copper_block cut_copper copper_grate copper_bulb copper_door_top copper_door_bottom copper_trapdoor'''.split()
METAL_COPPER_WEATHERED='''exposed_copper weathered_copper oxidized_copper exposed_cut_copper weathered_cut_copper oxidized_cut_copper waxed_copper waxed_exposed_copper waxed_weathered_copper waxed_oxidized_copper'''.split()
GEMS='''diamond_block emerald_block lapis_block amethyst_block budding_amethyst amethyst_cluster_large amethyst_cluster_medium amethyst_cluster_small'''.split()
SMOOTH='''quartz_block_side quartz_block_top quartz_block_bottom sea_lantern end_rod'''.split()
# Whole-texture emissive surfaces. Local lights add actual illumination; these values make the surfaces themselves radiate.
EMISSIVE_WARM='''glowstone shroomlight redstone_lamp_on furnace_front_on blast_furnace_front_on smoker_front_on campfire_log_lit ochre_froglight_side ochre_froglight_top'''.split()
EMISSIVE_COOL='''sea_lantern soul_lantern soul_torch soul_campfire_log_lit verdant_froglight_side verdant_froglight_top pearlescent_froglight_side pearlescent_froglight_top end_rod'''.split()
EMISSIVE_RED='''redstone_torch_on redstone_dust_line redstone_dust_cross'''.split()
SCULK='''sculk sculk_catalyst_side sculk_catalyst_top sculk_shrieker_side sculk_shrieker_top sculk_sensor_top'''.split()

write(STONE,[0,0,220,0]); write(POLISHED,[0,0,138,0]); write(EARTH,[0,0,196,18]); write(SAND,[0,0,226,18])
write(WOOD,[0,0,188,0]); write(FOLIAGE,[0,0,170,150]); write(FLOWERS,[0,0,175,175]); write(SNOW,[0,0,205,105])
write(GLASS,[0,0,30,0]); write(ICE,[0,0,42,72]); write(CERAMIC,[0,0,152,0])
write(METAL_IRON,[238,0,58,0]); write(METAL_GOLD,[255,0,38,0]); write(METAL_COPPER,[235,0,66,0]); write(METAL_COPPER_WEATHERED,[205,0,92,0])
write(GEMS,[0,0,52,18]); write(SMOOTH,[0,0,82,0])
write(EMISSIVE_WARM,[0,210,136,0]); write(EMISSIVE_COOL,[0,220,112,0]); write(EMISSIVE_RED,[0,170,160,0]); write(SCULK,[0,70,175,10])
print(f'Generated {len(list(OUT.glob("*.texture_set.json")))} per-texture PBR material overrides')
