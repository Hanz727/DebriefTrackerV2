import React from "react";
import '../Header.css'

const Header = () => {
    return (
        <div className="App-header">
            <img src={window.location.origin + '/img/logo.png'} alt="Logo"/>
            <h1>CVW-17 DATA VIEWER</h1>
        </div>
    )
}

export default Header