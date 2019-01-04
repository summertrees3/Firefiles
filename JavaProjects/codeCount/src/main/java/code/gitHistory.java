package code;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.PrintStream;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;

import org.eclipse.jgit.api.Git;
import org.eclipse.jgit.diff.DiffEntry;
import org.eclipse.jgit.diff.DiffFormatter;
import org.eclipse.jgit.diff.Edit;
import org.eclipse.jgit.diff.EditList;
import org.eclipse.jgit.diff.RawTextComparator;
import org.eclipse.jgit.errors.IncorrectObjectTypeException;
import org.eclipse.jgit.errors.MissingObjectException;
import org.eclipse.jgit.errors.StopWalkException;
import org.eclipse.jgit.lib.ObjectId;
import org.eclipse.jgit.lib.ObjectReader;
import org.eclipse.jgit.lib.Repository;
import org.eclipse.jgit.patch.FileHeader;
import org.eclipse.jgit.patch.HunkHeader;
import org.eclipse.jgit.revwalk.RevCommit;
import org.eclipse.jgit.revwalk.RevTree;
import org.eclipse.jgit.revwalk.RevWalk;
import org.eclipse.jgit.revwalk.filter.RevFilter;
import org.eclipse.jgit.treewalk.AbstractTreeIterator;
import org.eclipse.jgit.treewalk.CanonicalTreeParser;
import org.junit.Before;
import org.junit.Test;

import junit.framework.TestCase;

/**
 * @author dwg
 * @version V1.0
 * @date 2018��10��11��
 */
public class gitHistory extends TestCase {

	String gitFilePath = "E:\\quality-system";
	File root = new File(gitFilePath);
	Git git;
	Repository repository;

	@Before
	public void init() {
		try {
			git = Git.open(root);
			repository = git.getRepository();

		} catch (IOException e) {
			e.printStackTrace();
		}
	}

	@Test
	public void test() throws Exception {

		try {
			File file = new File("D://log//git3.log");
			PrintStream out = new PrintStream(file);
			System.setOut(out);
		} catch (FileNotFoundException e) {
			e.printStackTrace();
		}

		init();
//		RevWalk walk = new RevWalk(repository);
		List<RevCommit> commitList = new ArrayList<RevCommit>();
		// ��ȡ�ύ�ļ�¼
//		ObjectId objId = repository.resolve("refs/heads/remote/master");
		Iterable<RevCommit> commits = (Iterable<RevCommit>) git.log().setRevFilter(new RevFilter() {
			
			@Override
			public boolean include(RevWalk walker, RevCommit cmit)
					throws StopWalkException, MissingObjectException, IncorrectObjectTypeException, IOException {
				// TODO Auto-generated method stub
				return cmit.getAuthorIdent().getName().equals("zhangwei");
			}
			
			@Override
			public RevFilter clone() {
				// TODO Auto-generated method stub
				return null;
			}
		}).call();
		
//		System.out.println(git.log().call());

		for (RevCommit commit : commits) {
			commitList.add(commit);
		}

		String dateStart = "2018-10-01 00:00:00";

		for (int i = 0; i < commitList.size(); i++) {
			AbstractTreeIterator newTree = prepareTreeParser(commitList.get(i+1));
			
			AbstractTreeIterator oldTree = prepareTreeParser(commitList.get(i));
			
			List<DiffEntry> diff = git.diff().setNewTree(newTree).setOldTree(oldTree).setShowNameAndStatusOnly(true).call();
			

			ByteArrayOutputStream out = new ByteArrayOutputStream();
			DiffFormatter df = new DiffFormatter(out);
			// ���ñȽ���Ϊ���Կհ��ַ��Աȣ�Ignores all whitespace��
			df.setDiffComparator(RawTextComparator.WS_IGNORE_ALL);
			df.setRepository(git.getRepository());

			Date dateA = commitList.get(i).getAuthorIdent().getWhen();
			SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
			Date dateB = sdf.parse(dateStart);

			if (dateA.before(dateB)) {
				continue;
			}
			String sdfDate = sdf.format(dateA);
			System.out.println(commitList.get(i+1).getAuthorIdent().getName() + "|" + sdfDate);
			
//			System.out.println(diff);
			
			// ÿһ��diffEntry���ǵڸ��ļ��汾֮��ı䶯����
			for (DiffEntry diffEntry : diff) {
				
				df.format(diffEntry);
				String diffText = out.toString("UTF-8");
				String[] line = diffText.split("\n");
				String str = line[0].split("b/")[line[0].split("b/").length - 1];

//				 System.out.println(diffText);

				// ��ȡ�ļ�����λ�ã��Ӷ�ͳ�Ʋ������������������������������
				FileHeader fileHeader = df.toFileHeader(diffEntry);
				List<HunkHeader> hunks = (List<HunkHeader>) fileHeader.getHunks();
				int addLines = 0;
				int subLines = 0;
				for (HunkHeader hunkHeader : hunks) {
					EditList editList = hunkHeader.toEditList();
					for (Edit edit : editList) {
						addLines += edit.getEndA() - edit.getBeginA();
						subLines += edit.getEndB() - edit.getBeginB();

					}

				}
//				System.out.println("addLines=" + addLines + "\t" + "subLines=" + subLines + "\t" + str);
				System.out.println(addLines + "     "+ subLines + "\t" + str);

				out.reset();
			}
			System.out.println("---------------------------------------------");
		}

	}

	public AbstractTreeIterator prepareTreeParser(RevCommit commit) {
//		 System.out.println(commit.getId());
		try (RevWalk walk = new RevWalk(repository)) {
//			 System.out.println(commit.getTree().getId());
			RevTree tree = walk.parseTree(commit.getTree().getId());

			CanonicalTreeParser oldTreeParser = new CanonicalTreeParser();
			try (ObjectReader oldReader = repository.newObjectReader()) {
				oldTreeParser.reset(oldReader, tree.getId());
			}

			walk.dispose();

			return oldTreeParser;
		} catch (Exception e) {
			// TODO: handle exception
		}
		return null;
	}

}
