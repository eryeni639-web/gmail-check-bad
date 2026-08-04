def normalize_email(email: str) -> str:
    """
    Membersihkan email:
    - Hilangkan spasi
    - Ubah menjadi huruf kecil
    """
    return email.strip().lower()


def compare_emails(my_emails, bad_emails):
    """
    Membandingkan email milik user dengan daftar email bad.
    """

    my_set = {normalize_email(email) for email in my_emails if email.strip()}

    bad_set = {normalize_email(email) for email in bad_emails if email.strip()}

    matched = sorted(my_set.intersection(bad_set))

    good = sorted(my_set - bad_set)

    return {
        "matched": matched,
        "good": good,
        "total_my": len(my_set),
        "total_bad": len(bad_set),
        "matched_count": len(matched),
        "good_count": len(good),
    }
