import PropTypes from "prop-types";
import logo from "../assets/RD_grey2.png";
import "./Header.css";

export default function Header({ rightSlot = null }) {
    return (
        <header className="app-header">
            <div className="app-header__left">
                <a href="/">
                <img src={logo} alt="R&D" className="app-header__logo" />
                </a>
            </div>

            {/* FP and MR indicator here */}
            <div className="app-header__right">
                {rightSlot}
            </div>
        </header>
    );
}

Header.propTypes = {
    rightSlot: PropTypes.node,
};