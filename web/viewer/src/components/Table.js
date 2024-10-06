import React, {useEffect, useState} from "react";
import '../Table.css'

const Table = ({updateState}) => {
    const [data, setData] = useState({});

    useEffect(() => {
        const fetchData = async () => {
            try {
                const pilot_filter = document.getElementById("pilot").value;
                const rio_filter = document.getElementById("rio").value;
                const modex_filter = document.getElementById("modex").value;
                const weapon_type_filter = document.getElementById("weapon_type").value;
                const weapon_filter = document.getElementById("weapon").value;
                const killed_filter = document.getElementById("killed").value;

                const response = await fetch(`http://127.0.0.1:5000/get_db?pilot=${pilot_filter}&rio=${rio_filter}&modex=${modex_filter}&weapon_type=${weapon_type_filter}&weapon=${weapon_filter}&killed=${killed_filter}`);
                const rdata = await response.json();
                console.log(rdata);
                setData(rdata);
            } catch (err) {
               console.log(err);
            }
        }

        fetchData();

    }, [updateState])

    return (
        <div className="App-Table">

        </div>
    )
}

export default Table