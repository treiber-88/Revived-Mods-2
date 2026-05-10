WorldLoaded = function()
	players=Player.GetPlayers(function(p) return p end)
	table.remove(players) -- remove 'everyone'
	table.remove(players,1) -- remove 'neutral'
	table.remove(players,1) -- remove 'creeps'
end

Transports={}

Tick = function()
	local cossacks

end
