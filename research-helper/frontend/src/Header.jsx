import { HashLink as Link } from 'react-router-hash-link';

function Header(){

    return (
        <header id="header">
            <Link className="title-link">
                <span className="title-text">Research <span style={{ color: "#89CFF0"}}>Assistant</span></span>
            </Link>
        </header>
    )
}

export default Header;
