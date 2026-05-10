## Player
options-tech-level =
    .infantry-only = Infantry Only
    .low = Low
    .medium = Medium
    .high = High • Superweapons Off
    .unrestricted = High • Superweapons On

checkbox-kill-bounties =
    .label = Kill Bounties
    .description = Players receive cash bonuses when killing enemy units

checkbox-redeployable-mcvs =
    .label = Redeployable MCVs
    .description = Allow undeploying Construction Yard

checkbox-force-shield =
    .label = Force Shield
    .description = Grants all factions the Force Shield support power

checkbox-naval-units =
    .label = Naval Units
    .description = Enables naval units

checkbox-reveal-on-fire =
    .label = Reveal on Fire
    .description = Units reveal themselves when firing

checkbox-balanced-harvesting =
    .label = Balanced Harvesting
    .description = Enables dynamic harvester speed to account for the direction of resources relative to refineries

checkbox-fast-regrowth =
    .label = Fast Regrowth
    .description = Resources regrow at a faster rate

dropdown-queuetype =
    .label = Production Type
    .description = Single-Queue:\n  • TD / RA1 / TS / RA2 style\n  • One queue per production type\n  • Units created at primary building\n\nMulti-Queue:\n  • C&C3 / RA3 style\n  • One queue per production structure\n  • Upgrades remain single-queue\n\nCompetitive:\n  • Multi-Queue for units\n  • Single-Queue for structures & upgrades\n  • Multiple production structures of the same type have increased cost,\n    which is reduced after building radar/tech center

options-queuetype =
    .singlequeue = Single-Queue
    .multiqueuefull = Multi-Queue
    .multiqueuescaled = Competitive

## World
options-starting-units =
    .mcv-only = MCV Only
    .light-support = Light Support
    .heavy-support = Heavy Support

dropdown-difficulty =
    .label = Difficulty
    .description = The difficulty of the mission

options-difficulty =
    .easy = Easy
    .normal = Normal
    .hard = Hard

label-player-level = Current rank: { $level }
label-player-level-current-xp = Current XP: { $currentXp }
label-player-level-required-xp = Next rank XP: { $nextLevelXp }

label-player-influence-level = Influence level: { $level }
label-player-influence-level-time = Next level in { $time }
label-player-influence-coalition = Coalition: { $coalition }
label-player-influence-policy = Policy: { $policy }

## ObserverStatsLogic
options-observer-stats =
    .none = Information: None
    .basic = Basic
    .economy = Economy
    .production = Production
    .support-powers = Support Powers
    .combat = Combat
    .army = Army
    .upgrades = Upgrades
    .build-order = Build Order
    .units-produced = Units Produced
    .earnings-graph = Earnings (graph)
    .army-graph = Army Value (graph)
    .team-army-graph = Team Value (graph)

## Factions
faction-random =
    .name = Any
    .description = Random Faction\nA random faction will be chosen when the game starts.

faction-allies =
    .name = Allies

faction-england =
    .name = England
    .description = England: Subterfuge\n Units:\n  • Sniper\n  • Mirage Tank (replaces Scout Tank)\n  • Camo Pillbox (replaces Pillbox)\n\n Powers:\n  • Veil of War\n\n Upgrades:\n  • Raufoss Ammo\n\n Bonuses:\n  • Fake Buildings

faction-france =
    .name = France
    .description = France: Fortification\n Units:\n  • Battle Fortress\n  • Grand Cannon (replaces Prism Tower)\n\n Powers:\n  • Cluster Mines\n\n Upgrades:\n  • Entrenchment\n\n Bonuses:\n  • Walls & Defenses (10% Discount)

faction-germany =
    .name = Germany
    .description = Germany: Innovation\n Units:\n  • Chrono Prison\n  • Tank Destroyer\n\n Powers:\n  • Temporal Incursion\n  • Time Warp\n\n Upgrades:\n  • Temporal Flux\n\n Bonuses:\n  • Chrono Tanks (10% Discount)\n  • Chronosphere (20% Discount)

faction-usa =
    .name = USA
    .description = USA: Airborne Forces\n Units:\n  • SEAL\n  • Nighthawk (replaces Chinook)\n  • Guardian GI (via Airdrop)\n  • Grizzly Tank (via Airdrop)\n\n Powers:\n  • Strafing Run\n\n Upgrades:\n  • Advanced Airborne Training\n\n Bonuses:\n  • Airdrop Units

faction-soviet =
    .name = Soviet

faction-russia =
    .name = Russia
    .description = Russia: Tesla Technology\n Units:\n  • Tesla Tank\n  • Tesla Reactor (replaces Advanced Power Plant)\n\n Powers:\n  • Storm Troopers\n  • Parabombs\n\n Upgrades:\n  • Tesla Arcing\n\n Bonuses:\n  • Tesla Coil (10% Discount)\n  • Shock Trooper (10% Discount)\n  • Tesla Trooper (10% Discount)\n  • Kirov Tesla Bombs

faction-ukraine =
    .name = Ukraine
    .description = Ukraine: Demolition\n Units:\n  • Siege Tank\n  • Crazy Ivan (replaces Grenadier)\n\n Powers:\n  • Carpet Bomb\n  • Paratroopers\n\n Upgrades:\n  • Seismic Missiles\n\n Bonuses:\n  • V3 Launcher (10% Discount)\n  • Terror Dog (20% Discount)\n  • Kirov Cluster Bombs

faction-iraq =
    .name = Iraq
    .description = Iraq: Nuclear Warfare\n Units:\n  • Rad Trooper (replaces Shock Trooper)\n  • Toxin Tower (replaces Flame Tower)\n\n Powers:\n  • A-Bomb\n  • Paratroopers\n\n Upgrades:\n  • Desolator (replaces Rad Trooper)\n  • Eradicator (replaces Mammoth Tank)\n\n Bonuses:\n  • Demolition Truck (10% Discount)\n  • Missile Silo (40% Discount)\n  • Kirov Atom Bombs

faction-yuri =
    .name = Psi Corps
    .description = Psychic Corps: Mind Control & Genetics\n Units:\n  • Brute\n  • Floating Disc (replaces Kirov)\n  • Chaos Drone (replaces MAD Tank)\n  • Yuri (replaces Boris)\n\n Powers:\n  • Genetic Mutation Bomb\n  • Chaos Bombs\n\n Upgrades:\n  • Lasher Tank\n  • Gattling BTR

faction-gdi =
    .name = GDI

faction-talon =
    .name = Talon
    .description = Steel Talon: Mech Warfare\n Units:\n  • Wolverine\n  • Juggernaut\n  • Titan (replaces Mammoth Tank)\n\n Powers:\n  • X-O Drop\n\n Upgrades:\n  • Railgun Titan (replaces Titan)\n  • Gyro Stabilizers\n\n Bonuses:\n  • Tech Center (10% Discount)\n  • Upgrade Center (20% Discount)

faction-zocom =
    .name = ZOCOM
    .description = ZOCOM: Experimental Weapons\n Units:\n  • X-O Powersuit\n  • Disruptor\n  • Sonic Tower (replaces Advanced Guard Tower)\n\n Powers:\n  • Drop Pods\n  • Surgical Strike\n\n Upgrades:\n  • Ion Mammoth (replaces Mammoth Tank)\n  • Sonic Amplifiers\n\n Bonuses:\n  • Adv. Communication Center (40% Discount)\n  • Hazmat Suits Equipped as Standard

faction-eagle =
    .name = Eagle
    .description = Eagle Corps: Rapid Reaction Force\n Units:\n  • Pitbull\n  • Aurora\n  • Hover MLRS (replaces MLRS)\n\n Powers:\n  • Reinforcements\n\n Upgrades:\n  • Hover Mammoth (replaces Mammoth Tank)\n  • Orca Afterburner\n\n Bonuses:\n  • Aircraft (10% Discount)

faction-arc =
    .name = ARC
    .description = Advanced Robotics Command: Robotics\n Units:\n  • Mini Drone\n  • Jackknife\n  • Guardian Drone (replaces Hum-Vee)\n\n Powers:\n  • Nanite Repair\n\n Upgrades:\n  • Mammoth Drone (replaces Mammoth Tank)\n  • Battle Drone (replaces Battle Tank)\n\n Bonuses:\n  • Recon Drone (-20% Cooldown)\n  • Mobile Sensor Array (20% Discount)\n  • Drone Carrier (10% Discount)

faction-nod =
    .name = Nod

faction-blackh =
    .name = Black Hand
    .description = Black Hand: Flame Weaponry\n Units:\n  • Black Hand Trooper\n  • Heavy Flame Tank (replaces Flame Tank)\n\n Powers:\n  • Inferno Bomb\n  • Heavy Flame Tank Drop\n\n Upgrades:\n  • Black Napalm\n\n Bonuses:\n  • SSM (10% Discount)\n  • Free Howitzer Upgrade

faction-marked =
    .name = Marked of Kane
    .description = Marked of Kane: Alien Weaponry\n Units:\n  • Acolyte/Templar\n  • Venom (replaces Apache)\n\n Powers:\n  • Frenzy\n  • Subterranean Strike\n\n Upgrades:\n  • Quantum Capacitors\n\n Bonuses:\n  • Banshee (10% Discount)\n  • Temple Prime (10% Discount)

faction-legion =
    .name = Legion
    .description = Legion: Stolen Technology\n Units:\n  • Microwave Tank\n  • APC\n  • Battle Tank (replaces Light Tank)\n\n Powers:\n  • Cash Hack\n  • Technology Hack\n\n Upgrades:\n  • Intensified Microwaves\n\n Bonuses:\n  • Stolen Technology Units (10% Discount)\n  • Hack Satellite (-33% Cooldown)

faction-shadow =
    .name = Shadow
    .description = Shadow Sect: Stealth Technology\n Units:\n  • Mobile Stealth Generator\n  • Spectre (replaces SSM)\n\n Powers:\n  • Shadow Team\n  • Stealth Tank Drop\n\n Upgrades:\n  • Heavy Stealth Tank\n\n Bonuses:\n  • Comanche (10% Discount)\n  • Stealth Generator (+4 Passive Range)

faction-scrin =
    .name = Scrin

faction-reaper =
    .name = Reaper 17
    .description = Reaper-17: Frontal Assault\n Units:\n  • Stormcrawler\n  • Reaper Tripod (replaces Annihilator Tripod)\n\n Powers:\n  • Storm Spike\n\n Upgrades:\n  • Shard Walker\n\n Bonuses:\n  • Devourer (10% Discount)\n  • Ichor Seed (-20% Cooldown)

faction-traveler =
    .name = Traveler 59
    .description = Traveler-59: Fast Attack\n Units:\n  • Enervator\n  • Lacerator (replaces Seeker)\n\n Powers:\n  • Ion Surge\n\n Upgrades:\n  • Advanced Articulators\n\n Bonuses:\n  • Fast Walkers (+15% Speed)

faction-harbinger =
    .name = Harbinger 31
    .description = Harbinger-31: Heavy Weapons\n Units:\n  • Obliterator\n  • Marauder (replaces Intruder)\n\n Powers:\n  • Buzzer Swarm\n\n Upgrades:\n  • Stellar Fusion Cannon\n\n Bonuses:\n  • Devastator Warship (10% Discount)\n  • Mothership (10% Discount)

faction-collector =
    .name = Collector 73
    .description = Collector-73: Leeching & Degeneration\n Units:\n  • Atomizer\n  • Leecher (replaces Corrupter)\n\n Powers:\n  • Greater Coalescence\n\n Upgrades:\n  • Coalescence\n\n Bonuses:\n  • Field Manipulator (20% Discount)\n  • Suppression Field (-15% Cooldown, +10% Duration)

faction-eastsarconi =
    .name = East Sarconi
    .description = East Sarconi: Fast attack tactics\n Units:\n  • Evarian\n  • Fast Mammoth (replaces Anthracite Mammoth)\n\n Powers:\n  • Power of Speed\n\n All units have 10% more speed

faction-westsarconi =
    .name = West Sarconi
    .description = West Sarconi: Brute Force\n Units:\n  • Forest Menace\n  • Mordoc (Replaces Attack Spider)\n\n Powers:\n  • Strength in Numbers\n\n All units have 8% more strength

faction-randomallies =
    .name = Allies
    .description = Random Allied Faction\nA random Allied faction will be chosen when the game starts.

faction-randomsoviet =
    .name = Soviet
    .description = Random Soviet Faction\nA random Soviet faction will be chosen when the game starts.

faction-randomgdi =
    .name = GDI
    .description = Random GDI Faction\nA random GDI faction will be chosen when the game starts.

faction-randomnod =
    .name = Nod
    .description = Random Nod Faction\nA random Nod faction will be chosen when the game starts.

faction-randomscrin =
    .name = Scrin
    .description = Random Scrin Faction\nA random Scrin faction will be chosen when the game starts.

faction-randomsarconi =
    .name = Sarconi
    .description = Random Sarconi Faction\nA random Sarconi faction will be chosen when the game starts.

# ==================== CRIMSON CONFLICT FACTIONS ====================

faction-cc-allies-ext =
    .name = Crimson Conflict Allies

faction-kazakhstan =
    .name = Kazakhstan
    .description = Kazakhstan: Heavy Industry\n From Crimson Conflict\n Bonus:\n  • Specialized Artillery Units

faction-impjap =
    .name = Imperial Japan
    .description = Imperial Japan: Technological Superiority\n From Crimson Conflict\n Bonus:\n  • Advanced Aircraft

faction-china =
    .name = China
    .description = China: Overwhelming Numbers\n From Crimson Conflict\n Bonus:\n  • Mass-Produced Infantry

faction-israel =
    .name = Israel
    .description = Israel: Precision Warfare\n From Crimson Conflict\n Bonus:\n  • Advanced Defense Systems

faction-africa =
    .name = Africa

faction-chad =
    .name = Chad
    .description = Chad: Guerrilla Warfare\n From Crimson Conflict\n Bonus:\n  • Cheap Expendable Units

faction-angola =
    .name = Angola
    .description = Angola: Resource Control\n From Crimson Conflict\n Bonus:\n  • Enhanced Economy

faction-uganda =
    .name = Uganda
    .description = Uganda: Adaptive Tactics\n From Crimson Conflict\n Bonus:\n  • Versatile Infantry

faction-randomafrica =
    .name = Africa
    .description = Random African Faction\nA random African faction from Crimson Conflict will be chosen when the game starts.

