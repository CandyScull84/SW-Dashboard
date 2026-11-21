/*MergeDropdown.jsx*/
import PropTypes from "prop-types";
import "./MergeDropdown.css";
import useAutoScroll from "../hooks/useAutoScroll";

/**
 * MergeDropdown – show open merge requests in a dropdown.
 * When no merges a small NO MR ikon shows in header.
 */
export default function MergeDropdown({ merges, autoScroll }) {
    const listRef = useAutoScroll(autoScroll, 0.25, 50, [merges]);

    if (!merges?.length) {
        return (
            <div className="merge__icon--wrapper" title="No open merge requests">
                {/* <span className="merge__icon">🔀</span> */}
            </div>
        );
    }
    console.log("merge autoscroll =", autoScroll);
    console.log("merge listRef.current", listRef.current);
    return (
        <div className="merge__dropdown">
            <h3 className="merge__title">Merge Requests <span className="merge__count">{merges.length}</span></h3>
            <ul className="merge__list" ref={listRef}>
                {merges.map((m, i) => (
                    <li key={`${m.id}-${i}`} className="merge__row">
                        <a
                            href={m.web_url || "#"}
                            target="_blank"
                            rel="noreferrer"
                            className="merge__link"
                        >
                            <span className="merge__main">
                                {m.title || "(Untitled Merge Request)"}
                            </span>
                        </a>

                        <span className="merge__meta">
                            {m.author?.name || "Unknown"} → {" "}
                            {m.assignee?.name || "Unassigned"}
                        </span>

                        {/* <span className="merge__project">
                            {m.project_fullpath || "Unknown"} - ID: {m.project_id}
                        </span> */}
                    </li>
                ))}
            </ul>
        </div>
    );
}

MergeDropdown.propTypes = {
    merges: PropTypes.arrayOf(
        PropTypes.shape({
            id: PropTypes.number,
            title: PropTypes.string,
            web_url: PropTypes.string,
        })
    ),
    autoScroll: PropTypes.bool,
};
