# type: ignore
# MIT License
#
# Copyright (c) 2018-2019 Red Hat, Inc.

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from typing import List, Optional, Match, Any, TypeVar

from ogr.abstract import GitService, GitProject, PRComment, GitUser, IssueComment
from ogr.parsing import parse_git_repo
from ogr.utils import search_in_comments, filter_comments


Comment = TypeVar("Comment", IssueComment, PRComment)


class BaseGitService(GitService):
    def get_project_from_url(self, url: str) -> "GitProject":
        repo_url = parse_git_repo(potential_url=url)
        project = self.get_project(repo=repo_url.repo, namespace=repo_url.namespace)
        return project


class BaseGitProject(GitProject):
    @property
    def full_repo_name(self) -> str:
        """
        Get repo name with namespace
        e.g. 'rpms/python-docker-py'

        :return: str
        """
        return f"{self.namespace}/{self.repo}"

    @staticmethod
    def __get_comments(
        comments: List[Comment], filter_regex: str, reverse: bool, author: str
    ) -> List[Comment]:
        if reverse:
            comments.reverse()
        if filter_regex or author:
            comments = filter_comments(comments, filter_regex, author)
        return comments

    def get_pr_comments(
        self, pr_id, filter_regex: str = None, reverse: bool = False, author: str = None
    ) -> List[PRComment]:
        """
        Get list of pull-request comments.

        :param pr_id: int
        :param filter_regex: filter the comments' content with re.search
        :param reverse: reverse order of comments
        :param author: filter comments by author
        :return: [PRComment]
        """
        all_comments = self._get_all_pr_comments(pr_id=pr_id)
        return self.__get_comments(all_comments, filter_regex, reverse, author)

    def get_issue_comments(
        self,
        issue_id,
        filter_regex: str = None,
        reverse: bool = False,
        author: str = None,
    ) -> List[IssueComment]:
        """
        Get list of issue comments.

        :param pr_id: int
        :param filter_regex: filter the comments' content with re.search
        :param reverse: reverse order of comments
        :param author: filter comments by author
        :return: [PRComment]
        """
        all_comments = self._get_all_issue_comments(issue_id=issue_id)
        return self.__get_comments(all_comments, filter_regex, reverse, author)

    def search_in_pr(
        self,
        pr_id: int,
        filter_regex: str,
        reverse: bool = False,
        description: bool = True,
    ) -> Optional[Match[str]]:
        """
        Find match in pull-request description or comments.

        :param description: bool (search in description?)
        :param pr_id: int
        :param filter_regex: filter the comments' content with re.search
        :param reverse: reverse order of comments
        :return: re.Match or None
        """
        all_comments: List[Any] = self.get_pr_comments(pr_id=pr_id, reverse=reverse)
        if description:
            description_content = self.get_pr_info(pr_id).description
            if reverse:
                all_comments.append(description_content)
            else:
                all_comments.insert(0, description_content)

        return search_in_comments(comments=all_comments, filter_regex=filter_regex)


class BaseGitUser(GitUser):
    pass
