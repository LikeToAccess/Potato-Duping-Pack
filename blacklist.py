blacklist = [
	"bedrock","potato","poisonous_potato","lava","water","air",
	"farmland","tipped_arrow","bow","trident","crossbow",
	"elytra","shield","dead_bush","end_portal_frame",
	"turtle_egg","flint_and_steel","saddle","dragon_egg",
	"fishing_rod","shears","command_block","spectral_arrow",
	"barrier"
]
blacklist_fuzzy = [
	"netherite","music_disc","potion","_helmet",
	"_chestplate","_sword","_pickaxe","_leggings","_hoe","_axe",
	"_horse_armor","head","map","shovel","boots","_book","bed",
	"stew","soup","pattern","_bucket","_minecart","_a_stick",
	"_anvil","gold","boat","shulker_box","bell","void","command",
	"skull","zombie_horse","zombie_pigman","villager"
]

"""whitelist overrides blacklist"""
whitelist_fuzzy = [
	"apple"
]

"""number of items recieved per pospot"""
item_counts32 = [
	"emerald"
]
item_counts16_fuzzy = [
	"ender_pearl","snowball","bucket","honey_bottle",
	"_banner","_sign","beacon","nether_star","end_crystal",
	"armor_stand","redstone_block","iron_block","ender_chest",
	"_ore","name_tag","phantom_membrane"
]
item_counts8_fuzzy = [
	"conduit","lapis_block","emerald_block","diamond_block",
	"sea_pickle"
]
item_counts3_fuzzy = [
	"totem_of_undying","experience_bottle","emerald_block"
]

"""number of pospots needed"""
item_counts_inverse64_fuzzy = [
	"spawner"
]
item_counts_inverse32_fuzzy = [
	"spawn_egg"
]

if __name__ == "__main__":
	print(
		"""
		Blacklists: \"{}\", \"{}\"
		Blacklists (fuzzy): \"{}\", \"{}\", \"{}\", \"{}\"
		Whitelists (fuzzy): \"{}\"
		""".replace("\t","").format(
			blacklist,item_counts32,
			blacklist_fuzzy,item_counts16_fuzzy,
			item_counts8_fuzzy,item_counts3_fuzzy,
			whitelist_fuzzy
		)
	)
