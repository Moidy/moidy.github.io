import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def wait_for(driver, css_selector, timeout=10):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
    )


class TestPageLoad:
    def test_title_contains_moiders(self, page):
        assert "Moiders" in page.title

    def test_meta_description_present(self, page):
        meta = page.find_element(By.CSS_SELECTOR, 'meta[name="description"]')
        assert meta.get_attribute("content")


class TestNavigation:
    def test_nav_has_about_link(self, page):
        nav = wait_for(page, ".site-nav nav")
        links = nav.find_elements(By.TAG_NAME, "a")
        hrefs = [l.get_attribute("href") for l in links]
        assert any("#about" in h for h in hrefs)

    def test_nav_has_projects_link(self, page):
        nav = wait_for(page, ".site-nav nav")
        links = nav.find_elements(By.TAG_NAME, "a")
        hrefs = [l.get_attribute("href") for l in links]
        assert any("#projects" in h for h in hrefs)

    def test_nav_has_contact_link(self, page):
        nav = wait_for(page, ".site-nav nav")
        links = nav.find_elements(By.TAG_NAME, "a")
        hrefs = [l.get_attribute("href") for l in links]
        assert any("#contact" in h for h in hrefs)

    def test_nav_logo_visible(self, page):
        logo = wait_for(page, ".nav-logo")
        assert logo.is_displayed()


class TestHero:
    def test_hero_heading_visible(self, page):
        h1 = wait_for(page, ".hero h1")
        assert h1.is_displayed()

    def test_hero_cta_button_points_to_projects(self, page):
        btn = wait_for(page, ".hero .btn-primary")
        assert "#projects" in btn.get_attribute("href")


class TestAbout:
    def test_about_section_exists(self, page):
        section = page.find_element(By.ID, "about")
        assert section

    def test_skill_pills_present(self, page):
        pills = page.find_elements(By.CSS_SELECTOR, ".skill-pills .pill")
        assert len(pills) >= 5

    def test_stat_cards_present(self, page):
        stats = page.find_elements(By.CSS_SELECTOR, ".stat-card")
        assert len(stats) == 3


class TestContact:
    def test_github_link_present(self, page):
        link = page.find_element(By.CSS_SELECTOR, 'a[href*="github.com"]')
        assert link.get_attribute("href")

    def test_twitch_link_present(self, page):
        link = page.find_element(By.CSS_SELECTOR, 'a[href*="twitch.tv"]')
        assert link.get_attribute("href")

    def test_contact_links_open_in_new_tab(self, page):
        links = page.find_elements(By.CSS_SELECTOR, ".contact-link")
        for link in links:
            assert link.get_attribute("target") == "_blank"
            assert link.get_attribute("rel") and "noopener" in link.get_attribute("rel")
