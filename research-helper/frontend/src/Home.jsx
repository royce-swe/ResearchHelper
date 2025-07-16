import { useState, useEffect } from "react";

const words = [
  "Assistant.",
  "Helper.",
  "Partner.",
  "Companion.",
  "Navigator.",
  "Ally.",
];

function Home() {
  const [displayedText, setDisplayedText] = useState("");
  const [wordIndex, setWordIndex] = useState(0);
  const [charIndex, setCharIndex] = useState(0);
  const [isDeleting, setIsDeleting] = useState(false);
  const [userMajor, setUserMajor] = useState("");
  const [userSchool, setUserSchool] = useState("");
  const [facultyEmails, setFacultyEmails] = useState([]);
  const [emailOffset, setEmailOffset] = useState(0);
  const [hasMoreEmails, setHasMoreEmails] = useState(true);

  useEffect(() => {
    const currentWord = words[wordIndex];
    const typingSpeed = isDeleting ? 40 : 80;

    const timeout = setTimeout(() => {
      if (isDeleting) {
        setDisplayedText(currentWord.substring(0, charIndex - 1));
        setCharIndex((prev) => prev - 1);
      } else {
        setDisplayedText(currentWord.substring(0, charIndex + 1));
        setCharIndex((prev) => prev + 1);
      }

      if (!isDeleting && charIndex === currentWord.length) {
        setTimeout(() => setIsDeleting(true), 1000);
      }

      if (isDeleting && charIndex === 0) {
        setIsDeleting(false);
        setWordIndex((prev) => (prev + 1) % words.length);
      }
    }, typingSpeed);

    return () => clearTimeout(timeout);
  }, [charIndex, isDeleting, wordIndex]);

  // Helper to fetch emails with offset
  const fetchEmails = async (school, offset) => {
    try {
      const response = await fetch("http://localhost:5050/get-emails", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ school, offset }),
      });

      const data = await response.json();
      return data.emails || [];
    } catch (error) {
      console.error("Fetch failed:", error);
      return null;
    }
  };

  // Submit initial request, reset offset & emails
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!userSchool) return;

    const emails = await fetchEmails(userSchool, 0);
    if (emails === null) {
      setFacultyEmails(["Server error. Please try again later."]);
      setHasMoreEmails(false);
    } else {
      setFacultyEmails(emails);
      setEmailOffset(emails.length);
      setHasMoreEmails(emails.length === 3); // if less than 3, no more emails
    }
  };

  // Load more emails on button click
  const handleLoadMore = async () => {
    const moreEmails = await fetchEmails(userSchool, emailOffset);
    if (moreEmails === null) {
      setFacultyEmails((prev) => [...prev, "Server error. Please try again later."]);
      setHasMoreEmails(false);
      return;
    }
    setFacultyEmails((prev) => [...prev, ...moreEmails]);
    setEmailOffset((prev) => prev + moreEmails.length);
    if (moreEmails.length < 3) setHasMoreEmails(false);
  };

  return (
    <>
      <div className="typing-text" style={{ textAlign: "center" }}>
        <h1>
          Research
          <span style={{ color: "#89CFF0" }}>
            <em> {displayedText}</em>
          </span>
          <span className="cursor">|</span>
        </h1>
      </div>

      <div
        className="input-container"
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          marginTop: "2rem",
        }}
      >
        <form
          onSubmit={handleSubmit}
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: "1rem",
            width: "100%",
            maxWidth: "400px",
          }}
        >
          <h2>List Your Intended Field of Study</h2>
          <input
            type="text"
            placeholder="Ex. Computer Science"
            value={userMajor}
            onChange={(e) => setUserMajor(e.target.value)}
            style={{ width: "100%", padding: "0.5rem", textAlign: "center" }}
          />
          {userMajor && <p>{userMajor}</p>}

          <h2>Please Select Your School</h2>
          <select
            value={userSchool}
            onChange={(e) => setUserSchool(e.target.value)}
            style={{ width: "100%", padding: "0.5rem", textAlign: "center" }}
          >
            <option value="">-- Choose a School --</option>
            <option value="Stanford">Stanford University</option>
            <option value="UIUC">University of Illinois Urbana-Champaign</option>
            <option value="Purdue">Purdue University</option>
            <option value="Georgia Tech">Georgia Tech</option>
          </select>
          {userSchool && <p>Selected: {userSchool}</p>}

          <button type="submit" style={{ padding: "0.6rem 1.2rem" }}>
            Submit!
          </button>
        </form>

        {facultyEmails.length > 0 && (
          <div style={{ marginTop: "2rem", textAlign: "center" }}>
            <h3>Top Faculty Emails:</h3>
            <ul style={{ listStylePosition: "inside", padding: 0 }}>
              {facultyEmails.map((email, index) => (
                <li key={index}>{email}</li>
              ))}
            </ul>
            {hasMoreEmails && (
              <button onClick={handleLoadMore} style={{ marginTop: "1rem", padding: "0.5rem 1rem" }}>
                Load More
              </button>
            )}
          </div>
        )}
      </div>
    </>
  );
}

export default Home;
