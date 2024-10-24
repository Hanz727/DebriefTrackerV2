local Logger = {}

local userProfile = os.getenv("USERPROFILE")

local on_hit_events = {}
local on_shot_events = {}
local on_kill_events = {}

function Logger.print(text)
    trigger.action.outText(tostring(text), 10)
end

function Logger.logEvent(event, event_name)
    -- Check if event initiated by a player
    if event.initiator ~= nil and event.initiator:getPlayerName() ~= nil then
        -- Set all variables to defaults
        event.INITIATOR_NAME = event.initiator:getPlayerName()
        event.TARGET_DNAME = "target is nil"
        event.TARGET_TNAME = "target is nil"
        event.WEAPON_DNAME = "weapon is nil"
        local PILOT_NAME = "NONE"

        -- Get target name
        if event.target ~= nil then
            event.TARGET_TNAME = event.target:getDesc().typeName
            event.TARGET_DNAME = event.target:getDesc().displayName
        end

        -- Get weapon name (from desc)
        if event.weapon ~= nil then
            event.WEAPON_DNAME = event.weapon:getDesc().displayName
            event.WEAPON_TNAME = event.weapon:getDesc().typeName
        end
		
        -- Get the name only
        if #event.initiator:getPlayerName():split("|") == 3 then
            PILOT_NAME = event.initiator:getPlayerName():split("|")[3]:gsub("%s+", "")
        end

        -- Save events to according files
        if event_name == "on_shot_event" then
            on_shot_events[#on_shot_events+1] = event
            table.save(event, userProfile .. "\\Desktop\\DiscordBot\\Logs\\" .. #on_shot_events .. "_" .. os.date("%Y-%m-%d-%H%M") .. "_" .. PILOT_NAME .. "_on_shot_event.lua")
            table.save(event.weapon:getDesc(), userProfile .. "\\Desktop\\DiscordBot\\Weapons\\" .. event.weapon_name .. ".lua")
        elseif event_name == "on_hit_event" then
            on_hit_events[#on_hit_events+1] = event
            table.save(event, userProfile .. "\\Desktop\\DiscordBot\\Logs\\" .. #on_hit_events .. "_" .. os.date("%Y-%m-%d-%H%M") .. "_" .. PILOT_NAME .. "_on_hit_event.lua")
        elseif event_name == "on_kill_event" then
            on_kill_events[#on_kill_events+1] = event
            table.save(event, userProfile .. "\\Desktop\\DiscordBot\\Logs\\" .. #on_kill_events .. "_" .. os.date("%Y-%m-%d-%H%M") .. "_" .. PILOT_NAME .. "_on_kill_event.lua")
        end
    end
end

return Logger