require('os')

-- USER PATH
local userProfile = os.getenv("USERPROFILE")

-- Add all subfiles to path
package.path = userProfile .. "\\Desktop\\DiscordBot\\MissionScripts\\?.lua;" .. package.path

-- OUTPUT FILE PATH
local MISSIONDATA_PATH = userProfile .. "\\Desktop\\DiscordBot\\MissionData\\" .. os.date("%Y-%m-%d-%H%M") .. "_MissionData.json"

-- OTHER FILES
local Utils = require("DebriefTrackerUtils")
local Logger = require("DebriefTrackerLogger")
local table = require("DebriefTrackerTable")
local string = require("DebriefTrackerString")

local MainEventHandler = {}
local DATABASE = {}

local function isValidEvent(event)
    local base = event.weapon ~= nil and event.initiator ~= nil and event.initiator:getPlayerName() ~= nil
    if event.id == world.event.S_EVENT_SHOT then
        return base
    end
    return base and event.target ~= nil
end

local function isActuallyAG(event)
    local exceptions = {"AGM-65F", "AGM-65D", "AGM-65B", "AGM-84D"}
    for _, e in ipairs(exceptions) do
        if event.weapon:getDesc().displayName == e then
            return true
        end
    end
	return false
end

local function isAirToAir(weapon)
    return weapon:getDesc().category == 1
end

local function addAirToAirSHOT(event)
    local ANGELS = 0
    local ANGELS_TGT = 0
    local RANGE = 0
    local TGT_NAME = 0
    local TGT_TNAME = 0
    local WEAPON_NAME = event.weapon:getDesc().displayName
    local WEAPON_TNAME = event.weapon:getDesc().typeName

    local DL_CALLSIGN = "UNKNOWN"
    local TAIL_NUMBER = "UNKNOWN"
    local PILOT_NAME = ""
	local RIO_NAME = ""
    if #event.initiator:getPlayerName():split("|") == 3 then
        DL_CALLSIGN = event.initiator:getPlayerName():split("|")[1]:gsub("%s+", "")
        TAIL_NUMBER = event.initiator:getPlayerName():split("|")[2]:gsub("%s+", "")
        PILOT_NAME = event.initiator:getPlayerName():split("|")[3]:gsub("%s+", "")
    
		for i, player in ipairs(net.get_player_list()) do
			if #net.get_name(player):split("|") == 3 and net.get_name(player):split("|")[3]:gsub("%s+", "") ~= PILOT_NAME and net.get_name(player):split("|")[1]:gsub("%s+", "") == DL_CALLSIGN and net.get_name(player):split("|")[2]:gsub("%s+", "") == TAIL_NUMBER then
				RIO_NAME = net.get_name(player):split("|")[3]:gsub("%s+", "")
			end
		end
		
	end

    local lat, lon, alt = coord.LOtoLL(event.initiator:getPoint())
    ANGELS = alt * 3.281 / 1000

    local vel = event.initiator:getVelocity()
    local SPEED = Utils.calculateMachNumber(vel.x,vel.y,vel.z, Utils.calculateSpeedOfSound(event.initiator:getPoint()))

    local target = event.weapon:getTarget()
    if target ~= nil then
        local lat_tgt, lon_tgt, alt_tgt = coord.LOtoLL(target:getPoint())
        ANGELS_TGT = alt_tgt * 3.281 / 1000
        RANGE = Utils.haversine(lat, lon, lat_tgt, lon_tgt)
        TGT_NAME = target:getDesc().displayName
        TGT_TNAME = target:getDesc().typeName
        
        --unitpos = event.initiator:getPosition()
        --heading = (math.deg(math.atan2(unitpos.x.z, unitpos.x.x)) + 360) % 360
        --bearing = Utils.calculateInitialBearing(lat, lon, lat_tgt, lon_tgt) 
        --offset = math.abs(heading - bearing)
        
        if string.len(TGT_NAME) == 0 then
            TGT_NAME = TGT_TNAME
        end

        DATABASE[#DATABASE+1] =
         {TYPE = 1,
          time=event.time,
          initiator = event.initiator,
          target=target,
          weapon = event.weapon,
          WEAPON_NAME=WEAPON_NAME,
          WEAPON_TNAME=WEAPON_TNAME,
          DL_CALLSIGN=DL_CALLSIGN,
          TAIL_NUMBER=TAIL_NUMBER,
          PILOT_NAME=PILOT_NAME,
          RIO_NAME=RIO_NAME,
          TGT_NAME=TGT_NAME,
          TGT_TNAME=TGT_TNAME,
          SPEED=SPEED,
          ANGELS=ANGELS,
          ANGELS_TGT=ANGELS_TGT,
          RANGE=RANGE,
          DESTROYED=false,
          HIT=false
        }
        Utils.writeJsonToFile(DATABASE, MISSIONDATA_PATH)
    end
end

local function addAirToAirHIT(event)
    -- Changes HIT parameter of a shot
    for i, shot in ipairs(DATABASE) do
        if shot.weapon ~= nil and shot.TYPE == 1 and event.weapon == shot.weapon and event.initiator:getID() == shot.initiator:getID() and shot.HIT == false then
            DATABASE[i].HIT = true

            TGT_NAME = event.target:getDesc().displayName
            TGT_TNAME = event.target:getDesc().typeName

            if string.len(TGT_NAME) == 0 then
                TGT_NAME = TGT_TNAME
            end

            DATABASE[i].TGT_NAME = TGT_NAME
            DATABASE[i].TGT_TNAME = TGT_TNAME
        end
    end
    -- UPDATE JSON FILE
    Utils.writeJsonToFile(DATABASE, MISSIONDATA_PATH)
end

local function addAirToAirKILL(event)
    for i, shot in ipairs(DATABASE) do
        if shot.weapon ~= nil and shot.TYPE == 1 and event.weapon == shot.weapon and event.initiator:getID() == shot.initiator:getID() and shot.DESTROYED == false then
            DATABASE[i].DESTROYED = true

            TGT_NAME = event.target:getDesc().displayName
            TGT_TNAME = event.target:getDesc().typeName

            if string.len(TGT_NAME) == 0 then
                TGT_NAME = TGT_TNAME
            end

            DATABASE[i].TGT_NAME = TGT_NAME
            DATABASE[i].TGT_TNAME = TGT_TNAME
        end
    end
    Utils.writeJsonToFile(DATABASE, MISSIONDATA_PATH)
end

local function addAmraamKILL(event)
    --[[
        Fixes weird behavior with weapon object being nil at times with AIM-120C
    --]]
    if event.weapon == nil and event.weapon_name == "AIM_120C" and event.initiator ~= nil and event.target ~= nil and event.initiator:getPlayerName() ~= nil then
        for i, shot in ipairs(DATABASE) do
            if shot.weapon ~= nil and shot.TYPE == 1 and event.target == shot.target and shot.weapon:isExist() == false and event.initiator:getID() == shot.initiator:getID() and shot.DESTROYED == false then
                DATABASE[i].DESTROYED = true
                DATABASE[i].HIT = true

                TGT_NAME = event.target:getDesc().displayName
                TGT_TNAME = event.target:getDesc().typeName

                if string.len(TGT_NAME) == 0 then
                    TGT_NAME = TGT_TNAME
                end

                DATABASE[i].TGT_NAME = TGT_NAME
                DATABASE[i].TGT_TNAME = TGT_TNAME
            end
        end
        Utils.writeJsonToFile(DATABASE, MISSIONDATA_PATH)
    end
end

local function addGunKILL(event)
    if event.weapon == nil and event.initiator ~= nil and event.target ~= nil and
    (string.sub(event.weapon_name, 1, 4) == "M_61" or string.sub(event.weapon_name, 1, 4) == "M-61" or string.sub(event.weapon_name, 1, 3) == "M61" or string.sub(event.weapon_name, 1, 3) == "M53" or string.sub(event.weapon_name, 1, 3) == "M56" or event.weapon_name == "") then
        local DL_CALLSIGN = "UNKNOWN"
        local TAIL_NUMBER = "UNKNOWN"
        local PILOT_NAME = ""
		local RIO_NAME = ""

        if #event.initiator:getPlayerName():split("|") == 3 then
            DL_CALLSIGN = event.initiator:getPlayerName():split("|")[1]:gsub("%s+", "")
            TAIL_NUMBER = event.initiator:getPlayerName():split("|")[2]:gsub("%s+", "")
            PILOT_NAME = event.initiator:getPlayerName():split("|")[3]:gsub("%s+", "")
    
			for i, player in ipairs(net.get_player_list()) do
				if #net.get_name(player):split("|") == 3 and net.get_name(player):split("|")[3]:gsub("%s+", "") ~= PILOT_NAME and net.get_name(player):split("|")[1]:gsub("%s+", "") == DL_CALLSIGN and net.get_name(player):split("|")[2]:gsub("%s+", "") == TAIL_NUMBER then
					RIO_NAME = net.get_name(player):split("|")[3]:gsub("%s+", "")
				end
			end
        end

        local vel = event.initiator:getVelocity()
        local SPEED = Utils.calculateMachNumber(vel.x,vel.y,vel.z, Utils.calculateSpeedOfSound(event.initiator:getPoint()))

        local lat, lon, alt = coord.LOtoLL(event.initiator:getPoint())
        ANGELS = alt * 3.281 / 1000

        local lat_tgt, lon_tgt, alt_tgt = coord.LOtoLL(event.target:getPoint())
        ANGELS_TGT = alt_tgt * 3.281 / 1000

        local RANGE = Utils.haversine(lat, lon, lat_tgt, lon_tgt)

        local TGT_TNAME = event.target:getDesc().typeName
        local TGT_NAME = event.target:getDesc().displayName

        if string.len(TGT_NAME) == 0 then
            TGT_NAME = TGT_TNAME
        end

        if RANGE < 5 then
            DATABASE[#DATABASE+1] = {TYPE = 1, time=event.time, initiator = event.initiator, target=event.target, weapon = event.weapon, WEAPON_NAME="GUN", WEAPON_TNAME=event.weapon_name, DL_CALLSIGN=DL_CALLSIGN, TAIL_NUMBER=TAIL_NUMBER, PILOT_NAME=PILOT_NAME, RIO_NAME=RIO_NAME, TGT_NAME=TGT_NAME, TGT_TNAME=TGT_TNAME, SPEED=SPEED, ANGELS=ANGELS, ANGELS_TGT=ANGELS_TGT, RANGE=RANGE, DESTROYED=true, HIT=true}
            Utils.writeJsonToFile(DATABASE, MISSIONDATA_PATH)
        end
    end
end


local ag_kill_times = {}

local function isAirToGround(weapon)
    -- missile: 1 | rocket: 2 | bomb: 3
    return weapon:getDesc().category == 3 or weapon:getDesc().category == 2
end

local function addAirToGroundSHOT(event)
    local DL_CALLSIGN = "UNKNOWN"
    local TAIL_NUMBER = "UNKNOWN"
    local PILOT_NAME = ""
	local RIO_NAME = ""

    if #event.initiator:getPlayerName():split("|") == 3 then
        DL_CALLSIGN = event.initiator:getPlayerName():split("|")[1]:gsub("%s+", "")
        TAIL_NUMBER = event.initiator:getPlayerName():split("|")[2]:gsub("%s+", "")
        PILOT_NAME = event.initiator:getPlayerName():split("|")[3]:gsub("%s+", "")
		
		for i, player in ipairs(net.get_player_list()) do
			if #net.get_name(player):split("|") == 3 and net.get_name(player):split("|")[3]:gsub("%s+", "") ~= PILOT_NAME and net.get_name(player):split("|")[1]:gsub("%s+", "") == DL_CALLSIGN and net.get_name(player):split("|")[2]:gsub("%s+", "") == TAIL_NUMBER then
				RIO_NAME = net.get_name(player):split("|")[3]:gsub("%s+", "")
			end
		end
		
    end

    local WEAPON_NAME = event.weapon:getDesc().displayName
    local WEAPON_TNAME = event.weapon:getDesc().typeName

    local TGT_NAME = "NONE"
    local TGT_TNAME = "NONE"

    local target = event.weapon:getTarget()
    if target ~= nil then
        TGT_NAME = target:getDesc().displayName
        TGT_NAME = target:getDesc().typeName
    end

    DATABASE[#DATABASE+1] = {TYPE = 0, time=event.time, initiator = event.initiator, target="NONE", weapon = event.weapon, WEAPON_NAME=WEAPON_NAME, WEAPON_TNAME=WEAPON_TNAME, DL_CALLSIGN=DL_CALLSIGN, TAIL_NUMBER=TAIL_NUMBER, PILOT_NAME=PILOT_NAME, RIO_NAME=RIO_NAME, TGT_NAME=TGT_NAME, TGT_TNAME=TGT_TNAME, SPEED=-1, ANGELS=-1, ANGELS_TGT=-1, RANGE=-1, DESTROYED=true, HIT=true}
    Utils.writeJsonToFile(DATABASE, MISSIONDATA_PATH)
end

local function addAirToGroundKILL(event, max_time)
    if (event.target ~= nil and event.initiator ~= nil and event.initiator:getPlayerName() ~= nil) == false then
        return
    end

    if Utils.has_value(ag_kill_times, event.time) then
        -- avoid assigning kill to incorrect event, this function is often called multiple times for the same kill
        return
    end
    
    if event.weapon_name ~= nil then
        for i, shot in ipairs(DATABASE) do
            local shotWpn = shot.WEAPON_TNAME
            local shotWpnSplit = shotWpn:split("%.")
            if shotWpnSplit ~= nil then
                shotWpn = shotWpnSplit[#shotWpnSplit]
            end

            local same_weapon = shotWpn == event.weapon_name

            if event.initiator:getID() == shot.initiator:getID() and same_weapon and shot.TGT_NAME == "NONE" and event.time - shot.time <= max_time then
                TGT_NAME = event.target:getDesc().displayName
                TGT_TNAME = event.target:getDesc().typeName
    
                if string.len(TGT_NAME) == 0 then
                    TGT_NAME = TGT_TNAME
                end
    
                DATABASE[i].TGT_NAME = TGT_NAME
                DATABASE[i].TGT_TNAME = TGT_TNAME

                ag_kill_times[#ag_kill_times+1] = event.time
                Utils.writeJsonToFile(DATABASE, MISSIONDATA_PATH)
                return
            end
        end
    end
end

local function onHit(event)
    if isValidEvent(event) == false then
        return
    end

    -- A/G kill/hit
    if isActuallyAG(event) or isAirToGround(event.weapon) then
        addAirToGroundKILL(event, 400) -- USE KILL FUNC SINCE IT ONLY ADDS A PROPER TARGET NAME
        return
    end

    -- A/A HIT
    if isAirToAir(event.weapon) then
        addAirToAirHIT(event)
        return
    end

end

local function onShot(event)
    if isValidEvent(event) == false then
        return
    end

    -- A/G employment
    if isActuallyAG(event) or isAirToGround(event.weapon) then
        addAirToGroundSHOT(event);
        return
    end

    -- A/A employment
    if isAirToAir(event.weapon) then
        addAirToAirSHOT(event)
        return
    end

end

local function onKill(event)
    if isValidEvent(event) and isAirToAir(event.weapon) and isActuallyAG(event) == false then
        addAirToAirKILL(event)
    end

    addGunKILL(event)

    if isActuallyAG == false then
        addAmraamKILL(event)
        return
    end

    if isAirToGround(event.weapon) or isActuallyAG(event) then
        addAirToGroundKILL(event, 400)
        return
    end
end

function MainEventHandler:onEvent(event)
    if event.id == world.event.S_EVENT_HIT then -- ON HIT EVENT
        onHit(event)
        Logger.logEvent(event, "on_hit_event")
    end

    if event.id == world.event.S_EVENT_KILL then -- ON KILL EVENT 
        onKill(event)
        Logger.logEvent(event, "on_kill_event")
    end

    if event.id == world.event.S_EVENT_SHOT then -- ON SHOT EVENT
        onShot(event)
        Logger.logEvent(event, "on_shot_event")
    end
	
end

local function main()
    env.info("DebriefTracker v2.7 is running!!!")
    net.send_chat("DebriefTracker v2.7 is running!!!", true)
    world.addEventHandler(MainEventHandler)
end

main()