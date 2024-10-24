import React, {useEffect, useState} from "react";
import {procentage} from "../utils";

const PerTargetStats = ({data}) => {
    const [targetStats, setTargetStats] = useState({});

    useEffect(() => {
        let newStats = {};
        data.filter((entry) => entry.target !== null && entry.target.length > 0 && entry.weapon_type === "A/A")
            .forEach((entry) => {
                const target = entry.target.toLowerCase();
                if (!(target in newStats)) newStats[target] = [0,0];

                if (entry.hit || entry.destroyed)
                    newStats[target][0] += entry.qty;
                newStats[target][1] += entry.qty;
            })

        const sortedStats = Object.entries(newStats).sort(([targetA, statsA], [targetB, statsB]) => {
            return statsB[0] - statsA[0];
        })


        newStats = Object.fromEntries(sortedStats)

        setTargetStats(newStats);
    }, [data])

    return (
        <div className="App-PerTargetStats">
            <table className="PerWeaponTable" border="1">
                <thead>
                <tr>
                    <th>Target</th>
                    <th>Kills</th>
                    <th>Shots</th>
                    <th>PK%</th>
                </tr>
                </thead>

                <tbody>
                {Object.entries(targetStats).map(([target, [kills, shots]], index) => (
                    <tr key={index}>
                        <td>{target}</td>
                        <td>{kills}</td>
                        <td>{shots}</td>
                        <td>{procentage(kills,shots)}</td>
                    </tr>
                ))}
                </tbody>
            </table>

        </div>
    )
}

export default PerTargetStats