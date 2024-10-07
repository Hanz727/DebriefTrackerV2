import React, {useEffect} from "react";
import '../Table.css'

const Table = ({updateState, data, setData}) => {
    useEffect(() => {
        const fetchData = async () => {
            try {
                const pilot_filter = document.getElementById("pilot").value;
                const rio_filter = document.getElementById("rio").value;
                const modex_filter = document.getElementById("modex").value;
                const target_filter = document.getElementById("target").value;
                const weapon_type_filter = document.getElementById("weapon_type").value;
                const weapon_filter = document.getElementById("weapon").value;
                const killed_filter = document.getElementById("killed").value;

                const response = await fetch(`https://debrief.virtualcvw17.com/get_db?pilot=${pilot_filter}&rio=${rio_filter}&modex=${modex_filter}&weapon_type=${weapon_type_filter}&weapon=${weapon_filter}&killed=${killed_filter}&target=${target_filter}`);

                let rdata = await response.json()
                setData(rdata.reverse());
            } catch (err) {
               console.log(err);
            }
        }

        fetchData();

    }, [updateState])

    return (
        <div className="App-Table">
            <table border="1" className="Db-Table">
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Event</th>
                        <th>Pilot</th>
                        <th>Rio</th>
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
                    <td>{entry.rio_name}</td>
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