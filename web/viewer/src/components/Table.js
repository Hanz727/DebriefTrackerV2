import React, {useEffect, useState} from "react";
import '../Table.css'

const Table = ({updateState, data, setData}) => {
    const [RioToggle, setRioToggle] = useState(true);
    const [fetchedData, setFetchedData] = useState([]);
    const [intervalId, setIntervalId] = useState(null);

    const handleRioToggle = (ndata) => {
        for (let entry of ndata) {
            if (entry.rio_name !== null && entry.rio_name.trim() !== '') {
                setRioToggle(true);
                return
            }
        }
        setRioToggle(false);
    }

    const filterEntry = (filter, field) => {
        if (filter === null)
            return false;
        if (field === null)
            field = '';

        if (typeof field !== 'string')
            field = field.toString();
        return !field.toLowerCase().startsWith(filter.toLowerCase());
    }

    const createFetchInterval = async () => {
        const response = await fetch("https://debrief.virtualcvw17.com/get_db");
        const fdata = await response.json();
        setFetchedData(fdata);

        setIntervalId(setInterval(async () => {
            const response = await fetch("https://debrief.virtualcvw17.com/get_db");
            const fdata = await response.json();
            setFetchedData(fdata);
        }, 30000))
    }

    useEffect(() => {
        const filterData = async () => {
            try {
                const pilot_filter = document.getElementById("pilot").value;
                const rio_filter = document.getElementById("rio").value;
                const modex_filter = document.getElementById("modex").value;
                const target_filter = document.getElementById("target").value;
                const weapon_type_filter = document.getElementById("weapon_type").value;
                const weapon_filter = document.getElementById("weapon").value;
                const killed_filter = document.getElementById("killed").value;

                if (intervalId === null)
                    await createFetchInterval();

                let rdata = fetchedData;
                rdata = rdata.filter(entry => {
                    if (entry.weapon_type === "N/A") return false;
                    if (filterEntry(pilot_filter, entry.pilot_name)) return false;
                    if (filterEntry(rio_filter, entry.rio_name)) return false;
                    if (filterEntry(modex_filter, entry.tail_number)) return false;
                    if (filterEntry(target_filter, entry.target)) return false;
                    if (filterEntry(weapon_type_filter, entry.weapon_type)) return false;
                    if (filterEntry(weapon_filter, entry.weapon)) return false;

                    return !(filterEntry(killed_filter, entry.hit) || filterEntry(killed_filter, entry.destroyed));
                })
                handleRioToggle(rdata);

                setData(rdata.reverse());
            } catch (err) {
               console.log(err);
            }
        }

        filterData();

    }, [updateState, fetchedData])

    return (
        <div className="App-Table">
            <table border="1" className="Db-Table">
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Event</th>
                        <th>Pilot</th>
                        {RioToggle && (
                            <th>Rio</th>
                        )}
                        <th>Weapon</th>
                        <th>Target</th>
                        <th>Range</th>
                        <th>Speed</th>
                        <th>Killed?</th>
                    </tr>
                </thead>
                <tbody>
                {data.map((entry, index) => (
                    <tr key={index}>
                    <td>{entry.date}</td>
                    <td>{entry.event}</td>
                    <td>{entry.pilot_name}</td>
                    {RioToggle && (
                        <td>{entry.rio_name}</td>
                     )}
                    <td>{entry.weapon ? entry.weapon : ""}</td>
                    <td>{entry.target ? entry.target : ""}</td>
                    <td>{entry.range ? entry.range : ""}</td>
                    <td>{entry.speed ? entry.speed : ""}</td>
                    <td>{entry.destroyed ? "True" : "False"}</td>
                    </tr>
                ))}
                </tbody>
            </table>
        </div>
    )
}

export default Table