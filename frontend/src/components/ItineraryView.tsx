import type { Itinerary, ItineraryChange, WeatherSource } from "../types/domain";

interface ItineraryViewProps {
  itinerary: Itinerary;
  changes?: ItineraryChange[];
  weatherSource?: WeatherSource | null;
}

function formatMoney(amount: number, currency: string): string {
  try {
    return new Intl.NumberFormat(undefined, {
      style: "currency",
      currency,
      currencyDisplay: "code",
      maximumFractionDigits: 0,
    }).format(amount);
  } catch {
    return `${currency} ${amount.toLocaleString()}`;
  }
}

export function ItineraryView({ itinerary, changes = [], weatherSource }: ItineraryViewProps) {
  return (
    <section className="itinerary" aria-labelledby="itinerary-title">
      <div className="itinerary-heading">
        <div>
          <p className="eyebrow">Your route, in days</p>
          <h2 id="itinerary-title">{itinerary.destination}</h2>
        </div>
        <dl className="trip-facts">
          <div>
            <dt>Days</dt>
            <dd>{itinerary.duration}</dd>
          </div>
          <div>
            <dt>Travellers</dt>
            <dd>{itinerary.travellers}</dd>
          </div>
          <div>
            <dt>Budget</dt>
            <dd>{formatMoney(itinerary.budget.amount, itinerary.budget.currency)}</dd>
          </div>
        </dl>
      </div>

      {weatherSource ? (
        <p className="weather-source" role="status">
          Weather source: <strong>{weatherSource}</strong>
        </p>
      ) : null}

      <div className="day-list">
        {itinerary.days.map((day) => (
          <section className="day-plan" key={day.day_number} aria-labelledby={`day-${day.day_number}`}>
            <div className="day-heading">
              <span className="day-number">{String(day.day_number).padStart(2, "0")}</span>
              <h3 id={`day-${day.day_number}`}>Day {day.day_number}</h3>
            </div>
            {day.activities.length === 0 ? (
              <p className="empty-day">{day.empty_reason}</p>
            ) : (
              <ul className="activity-list">
                {day.activities.map((activity) => (
                  <li className="activity" key={`${day.day_number}-${activity.time}-${activity.title}`}>
                    <time>{activity.time}</time>
                    <div className="activity-body">
                      <h4>{activity.title}</h4>
                      <p>{activity.description}</p>
                      <div className="activity-meta">
                        <span>{activity.location}</span>
                        <span>{formatMoney(activity.cost.amount, activity.cost.currency)}</span>
                        <span>{activity.location_type}</span>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </section>
        ))}
      </div>

      {changes.length > 0 ? (
        <section className="change-log" aria-labelledby="change-log-title">
          <h3 id="change-log-title">What changed</h3>
          <ul>
            {changes.map((change, index) => (
              <li key={`${change.day_number}-${change.original_activity}-${index}`}>
                <strong>Day {change.day_number}:</strong> {change.original_activity}
                {change.replacement_activity ? ` -> ${change.replacement_activity}. ` : ". "}
                {change.reason} <span>Source: {change.weather_source}</span>
              </li>
            ))}
          </ul>
        </section>
      ) : null}
    </section>
  );
}
