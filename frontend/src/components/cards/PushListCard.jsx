import PropTypes from "prop-types";
import "./PushListCard.css";
import useAutoScroll from "../../hooks/useAutoScroll";

export default function PushListCard({ pushes, autoScroll }) {
    const listRef = useAutoScroll(autoScroll);

    if (!pushes?.length) {
        return <p>No recent pushes...</p>;   
    }

    return (
        <ul className="push__list" ref={listRef}>
            {pushes.map((p, i) => (
                <li key={`${p.project_id}-${i}`} className="push__row">
                    {p.avatar_url ? (
                        <img
                            src={p.avatar_url}
                            alt={p.user_name || "User"}
                            className="push__avatar"
                        />
                    ):(
                        <div className="push__avatar push__avatar--fallback">
                            {p.user_name ? p.user_name[0].toUpperCase() : "?"}
                        </div>
                    )}
                    <div className="push__content">
                        <a
                            href={p.web_url || "#"}
                            target="_blank"
                            rel="noreferrer"
                            className="push__project"
                        >
                            {p.project_fullpath || p.project_name}
                        </a>
                        <span className="push__meta">
                            {p.user_name} {p.user_id ? `#${p.user_id}` : ""} — “{p.commit_title}”
                        </span>
                    </div>
                </li>
            ))}
        </ul>
    );
}

PushListCard.propTypes = {
    autoScroll:PropTypes.bool,
    pushes: PropTypes.arrayOf(
        PropTypes.shape({
            avatar_url: PropTypes.string,
            user_name: PropTypes.string,
            user_id: PropTypes.number,
            project_id: PropTypes.number,
            project_name: PropTypes.string,
            project_fullpath: PropTypes.string,
            web_url: PropTypes.string,
            commit_title: PropTypes.string,
        })
    ),
};
