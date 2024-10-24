local Utils = {}

function Utils.calculateSpeedOfSound(pos)
    local tempK, pressure = atmosphere.getTemperatureAndPressure(pos)
    local spd = 331.3*math.sqrt(tempK/273.15)
    return spd
end

function Utils.calculateMachNumber(velocityX, velocityY, velocityZ, speedOfSound)
    local velocityMagnitude = math.sqrt(velocityX^2 + velocityY^2 + velocityZ^2)
    local machNumber = velocityMagnitude / speedOfSound
    return machNumber
end

function Utils.has_value (tab, val)
    for _, value in ipairs(tab) do
        if value == val then
            return true
        end
    end

    return false
end

function Utils.calculateInitialBearing(lat1, lon1, lat2, lon2)
    local lat1_rad = math.rad(lat1)
    local lat2_rad = math.rad(lat2)
    local delta_lon = math.rad(lon2 - lon1)
    
    local y = math.sin(delta_lon) * math.cos(lat2_rad)
    local x = math.cos(lat1_rad) * math.sin(lat2_rad) - math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(delta_lon)
    
    local initial_bearing_rad = math.atan2(y, x)
    local initial_bearing_deg = math.deg(initial_bearing_rad) - 6.2
    
    -- Normalize the bearing to the range [0, 360)
    return (initial_bearing_deg + 360) % 360
end

function Utils.haversine(lat1, lon1, lat2, lon2)
    local R = 6371000 -- Earth's radius in meters (approximate)
    local NM_PER_METER = 0.0005399568 -- Nautical miles per meter

    local lat1_rad = math.rad(lat1)
    local lon1_rad = math.rad(lon1)
    local lat2_rad = math.rad(lat2)
    local lon2_rad = math.rad(lon2)

    local dlat = lat2_rad - lat1_rad
    local dlon = lon2_rad - lon1_rad

    local a = math.sin(dlat/2) * math.sin(dlat/2) +
              math.cos(lat1_rad) * math.cos(lat2_rad) *
              math.sin(dlon/2) * math.sin(dlon/2)

    local c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    local distance_meters = R * c
    local distance_nautical_miles = distance_meters * NM_PER_METER

    return distance_nautical_miles
end

function Utils.writeJsonToFile(database, filename)
    local jsonContent = ""
    for i, entry in ipairs(database) do
        local entryJson = string.format('{"TYPE": %d, "WEAPON_NAME": "%s", "DL_CALLSIGN": "%s", "TAIL_NUMBER": "%s", "PILOT_NAME": "%s", "RIO_NAME": "%s", "TGT_NAME": "%s", "TGT_TNAME": "%s", "SPEED": %.2f, "ANGELS": %d, "ANGELS_TGT": %d, "RANGE": %d, "DESTROYED": %s, "HIT": %s}',
            entry.TYPE, entry.WEAPON_NAME, entry.DL_CALLSIGN, entry.TAIL_NUMBER, entry.PILOT_NAME, entry.RIO_NAME, entry.TGT_NAME:gsub('"', '\\"'), entry.TGT_TNAME:gsub('"', '\\"'), entry.SPEED, entry.ANGELS, entry.ANGELS_TGT, entry.RANGE, tostring(entry.DESTROYED), tostring(entry.HIT))

        jsonContent = jsonContent .. entryJson
        if i < #database then
            jsonContent = jsonContent .. ","
        end
    end

    local file = io.open(filename, "w")
    if file then
        io.write(file, "[" .. jsonContent .. "]")
        io.flush(file)
        io.close(file)
        --print("Data has been written to " .. filename)
    else
        --print("Failed to open file for writing.")
    end
end

return Utils