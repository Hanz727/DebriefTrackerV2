import React, {useEffect, useState} from "react";
import '../PerWeaponStats.css'
import {procentage} from "../utils";
const PerWeaponStats = ({data, type}) => {
    const [wpnStats, setWpnStats] = useState({});

    useEffect(() => {
        //update
        let newStats = {};
        data.filter((entry) => entry.weapon !== null && entry.weapon_type === type)
            .forEach((entry) => {
                const weapon = entry.weapon
                if (!(weapon in newStats))
                    newStats[weapon] = [0, 0];

                if (entry.hit || entry.destroyed)
                    newStats[weapon][0] += entry.qty;
                newStats[weapon][1] += entry.qty;
        })

        const sortedStats = Object.entries(newStats).sort(([keyA, statsA], [keyB, statsB]) => {
            return keyA.localeCompare(keyB);
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
                    <th>Kills</th>
                    {type === "A/A" && (
                        <th>Shots</th>
                    )}
                    {type === "A/A" && (
                        <th>PK%</th>
                    )}
                </tr>
                </thead>

                <tbody>
                    {Object.entries(wpnStats).map(([weapon, [kills, shots]], index) => (
                      <tr key={index}>
                        <td>{weapon}</td>
                        <td>{kills}</td>
                        {type === "A/A" && (
                            <td>{shots}</td>
                        )}
                        {type === "A/A" && (
                            <td>{procentage(kills,shots)}</td>
                        )}

                      </tr>
                    ))}
                </tbody>
            </table>
        </div>
    )
}

export default PerWeaponStats