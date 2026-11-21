/*FailingPipelineIndicator*/
import PropTypes from "prop-types";
import "./FailingPipelinesIndicator.css";
import useAutoScroll from "../hooks/useAutoScroll";

export default function FailingPipelinesIndicator({ pipelines = [], autoScroll }) {
  const failing = pipelines.filter(p =>
    ["failed", "running", "pending", "canceled"].includes(p.status) &&
    !p.archived
  );

  const listRef = useAutoScroll(autoScroll);
  // ----------------------
  // NO FAILING PIPELINES
  // ----------------------
  if (failing.length === 0) {
    return (
      <div className="fp-indicator fp--none">
        <span>NO FP</span>
      </div>
    );
  }

  // ----------------------
  // FAILING PIPELINES CARD
  // ----------------------
  return (
    <div className="fp-card">
      <h3 className="fp-title">
        Failing Pipelines 
        <span className="pipe__count">{failing.length}</span>
      </h3>

      <div className="fp-list" ref={listRef}>
        {failing.map((p, i) => (
            <div key={i} className="fp-item">

            {/* RAD 1: Project + ID */}
            <div className="fp-row-top">
                <a
                href={p.web_url}
                target="_blank"
                rel="noopener noreferrer"
                className="fp-project"
                >
                {p.project_name}
                </a>
                <span className="fp-id">ID: {p.project_id}</span>
            </div>

            {/* RAD 2: Branch + Status */}
            <div className="fp-row-mid">
                <span className="fp-ref">branch: {p.ref}</span>
                <span className={`fp-status fp-${p.status}`}>
                Status: {p.status}
                </span>
            </div>

            {/* RAD 3: User + Timestamp */}
            <div className="fp-row-bottom">
                {p.user_name && (
                <span className="fp-user">by {p.user_name}</span>
                )}
                <span className="fp-time">
                {new Date(p.updated_at).toLocaleString("sv-SE", {
                    hour: "2-digit",
                    minute: "2-digit",
                    year: "numeric",
                    month: "2-digit",
                    day: "2-digit",
                })}
                </span>
            </div>

            </div>
        ))}
        </div>

    </div>
  );
}

FailingPipelinesIndicator.propTypes = {
  pipelines: PropTypes.arrayOf(
    PropTypes.shape({
      project_id: PropTypes.number,
      project_name: PropTypes.string,
      status: PropTypes.string.isRequired,
      ref: PropTypes.string,
      user_name: PropTypes.string,
      updated_at: PropTypes.string,
      web_url: PropTypes.string,
    })
  ).isRequired,
  autoScroll: PropTypes.bool,
};
