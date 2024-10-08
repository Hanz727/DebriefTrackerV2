import React, {useEffect, useState} from "react";
import '../PerWeaponStats.css'
import {procentage} from "../utils";
const PerWeaponStats = ({data, type}) => {
    const [wpnStats, setWpnStats] = useState({});

    useEffect(() => {
        let newStats = {};
        data.filter((entry) => entry.weapon !== null && entry.weapon_type === type)
            .forEach((entry) => {
                let weapon = entry.weapon
                if (weapon.startsWith("AIM-120"))
                    weapon = "AIM-120C"
                if (weapon.startsWith("AIM-9"))
                    weapon = "AIM-9"
                if (weapon.startsWith("AIM-7"))
                    weapon = "AIM-7"

                if (!(weapon in newStats))
                    newStats[weapon] = [0, 0];

                if ((entry.hit || entry.destroyed) || type === 'A/G')
                    newStats[weapon][0] += entry.qty;
                newStats[weapon][1] += entry.qty;
        })

        const sortedStats = Object.entries(newStats).sort(([keyA, statsA], [keyB, statsB]) => {
            return statsB[0] - statsA[0];
        })

        newStats = Object.fromEntries(sortedStats)
        setWpnStats(newStats);
    }, [data])

    return (
        <div className="App-PerWeaponStats">
            <table className="PerWeaponTable" border="1">
                <thead>
                <tr>
                    <th>Weapon</th>
                    {type === "A/A" ? (
                        <th>Kills< /th>
                    ) : (
                        <th>Drops< /th>
                    )}

                    {type === "A/A" && (
                        <>
                            <th>Shots</th>
                            <th>PK%</th>
                        </>
                    )}
                </tr>
                </thead>

                <tbody>
                    {Object.entries(wpnStats).map(([weapon, [kills, shots]], index) => (
                      <tr key={index}>
                        <td>{weapon}</td>
                        <td>{kills}</td>
                        {type === "A/A" && (
                            <>
                                <td>{shots}</td>
                                <td>{procentage(kills, shots)}</td>
                            </>
                        )}
                      </tr>
                    ))}
                </tbody>
            </table>
        </div>
    )
}

export default PerWeaponStats